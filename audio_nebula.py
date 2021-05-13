import pyaudio
import numpy as np
import sys, getopt
import os
from src.pyaudioanalysis.pyAudioAnalysis import ShortTermFeatures
from vispy import gloo, app
from vispy.util.transforms import perspective, translate, rotate
from vispy.gloo import Program
from multiprocessing import Manager, Process, Queue
from shader import vert, frag
from utils import save_settings, validate_settings, read_settings, get_setting, set_setting, clamp, toggle_color

# VisPy Visualization Canvas Class
class Canvas(app.Canvas):
    def __init__(self, sound_data_queue):
        app.Canvas.__init__(self, title='Audio Nebula', keys='interactive', size=(get_setting('width'), get_setting('height')))
        ps = 1

        # Initialize vertex data for default state. This data will be updated by incoming audio data
        # in realitime to change the way the vertices look and behave.
        self.particle_count = 1000
        self.data = np.zeros(self.particle_count, [('a_position', np.float32, 3),
                            ('a_bg_color', np.float32, 4),
                            ('a_fg_color', np.float32, 4),
                            ('a_size', np.float32)])
        self.data['a_position'] = 0.45 * np.random.randn(self.particle_count, 3)
        self.data['a_bg_color'] = 1, 1, 1, .5
        self.data['a_fg_color'] = 1, 1, 1, 0
        self.data['a_size'] = np.random.uniform(5*ps, 10*ps, self.particle_count)

        # Initialize canvas class attributes
        self.translate = 2.5
        self.program = gloo.Program(vert(), frag())
        self.projection = np.eye(4, dtype=np.float32)
        self.current_energy = 0
        self.theta = 0
        self.phi = 0
        self.intense_color = get_setting('intensity_color')
        self.sound_data_queue = sound_data_queue
        self.timer = app.Timer('auto', connect=self.on_timer, start=True)

        # Bind data to buffer and initialize program data
        self.program.bind(gloo.VertexBuffer(self.data))
        self.program['u_linewidth'] = 0
        self.program['u_antialias'] = 1.0
        self.program['u_model'] = np.eye(4, dtype=np.float32)
        self.program['u_view'] = translate((0, 0, -self.translate))
        self.program['u_size'] = 5 / self.translate

        gloo.set_state('translucent', clear_color='white')
        gloo.set_clear_color((0, 0, 0, 1))

        # Render visualization canvas
        self.show()


    # Key press events to drive user interactivity while the visualization is running
    def on_key_press(self, event):
        if event.text == 'q':
            self.close()
        # 'p' and 'o' will adjust mic sensitivity by applying a universal multiplier over
        # data attributes driven by incoming audio energy (amplitude) data.
        if event.text == 'p' and get_setting('mic_sensitivity') < .05:
            set_setting('mic_sensitivity', get_setting('mic_sensitivity') + .005)
        if event.text == 'o' and get_setting('mic_sensitivity') > 0:
            set_setting('mic_sensitivity', get_setting('mic_sensitivity') - .005)
        # 'c' will toggle color schemes by dictating whether high intensity audio data is
        # visualized by red or green in contrast with blue for low-intensity audio.
        if event.text == 'c':
            self.intense_color = toggle_color(self.intense_color)
            set_setting('intensity_color', self.intense_color)


    # Function to handle when the VisPy canvas window is resized by the user.
    def on_resize(self, event):
        gloo.set_viewport(0, 0, self.physical_size[0], self.physical_size[1])
        self.projection = perspective(45.0, self.size[0] /
                                      float(self.size[1]), 1.0, 1000.0)
        self.program['u_projection'] = self.projection


    # Function to handle drawing the VisPy visualization
    def on_draw(self, event):
        gloo.clear()
        self.program.draw('points')


    def on_timer(self, event):
        # Get sound data from queue
        sound_data = self.sound_data_queue.get()
        # get energy and frequency data, clamped and normalized as a multiplier value
        energy = clamp(sound_data['energy'], 0, 40) / 2
        frequency = clamp(sound_data['frequency'], 0, 20)

        # Only regiser a change in energy if the change is by greater than 2 in either direction.
        # This prevents a flicker effect from low-energy audio inputs like background noise
        # from a mic, which can make the visualization harder on the eyes.
        if abs(energy - self.current_energy) > 2:
            self.current_energy = energy

        # Drive the motion of the vertices by adjusting theta and pi values according to
        # audio energy level. Higher energy audio will cause larger increments of the
        # theta and pi values, creating the illusion of faster particle movement.
        self.theta += energy * get_setting('mic_sensitivity') * 10 + .25
        self.phi += energy * get_setting('mic_sensitivity') * 10 + .25

        self.model = np.dot(rotate(self.theta, (0, 0, 1)),
                            rotate(self.phi, (0, 1, 0)))
        self.program['u_model'] = self.model

        # Ignore frequency if total energy is below 2. This will prevent frequncy flicker that
        # sometimes occurs when there is minimal audio input to analyize.
        if energy < 2:
            frequency = 0

        # Adjust particle size according to frequency. This, along with adjusting the alpha below,
        # creates the visual effect of particles shifting in and out of focus.
        self.data['a_size'] = 15 - (frequency / 2)

        # Adjust particle color based on energy, plus alpha based on frequency. The blue channel
        # acts as the universal interpretation of low-energy audio, with either red or green representing
        # high-energy audio depending on user preference. A calculation converts the energy and frequency
        # inputs into an RGBA object and updates the color property in the data structure accordingly.
        if self.intense_color == 'red':
            self.data['a_bg_color'] = (
                0 + clamp(self.current_energy * get_setting('mic_sensitivity'), .1, .9), #R
                0,                                                                       #G
                1 - clamp(self.current_energy * get_setting('mic_sensitivity'), .1, .9), #B
                .3 + (frequency / 50)                                                    #A
            )
        elif self.intense_color == 'green':
            self.data['a_bg_color'] = (
                0,                                                                       #R
                0 + clamp(self.current_energy * get_setting('mic_sensitivity'), .1, .9), #G
                1 - clamp(self.current_energy * get_setting('mic_sensitivity'), .1, .9), #B
                .3 + (frequency / 50)                                                    #A
            )

        # Rebind the updated data attribute and trigger an update to the visualization canvas.
        self.program.bind(gloo.VertexBuffer(self.data))
        self.update()


# Stream audio from user's mic input
def start_recording(sound_data_queue):
    # Initilalize audio input settings and constants
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    CHUNK = 1024

    # Initialize PyAudio
    audio = pyaudio.PyAudio()

    # Start autio stream
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                rate=RATE, input=True,
                frames_per_buffer=CHUNK)

    # Infinite loop to stream incoming audio one sample of bytes at a time. Each sample is processed
    # and parsed into a data structure which is passed into the queue for the visualizer to render.
    while(True):
        # Read audio data from stream
        data = stream.read(CHUNK)
        signal = np.frombuffer(data, dtype=np.int16)

        # Temporarily suppress stdout to prevent debug print statements in pyAudioAnalysis source 
        # code from flooding console output.
        sys.stdout = open(os.devnull, "w")
  
        # Get raw frequency data for sample via pyAudioAnalysis spetrogram function
        F, time, freq = ShortTermFeatures.spectrogram(signal, RATE, window=0.050*(RATE/CHUNK), step=0.025*(RATE/CHUNK))
   
        # Re-enable stdout
        sys.stdout = sys.__stdout__

        # Get raw energy data for sample via pyAudioAnalysis energy function, divided by 100 and clamped
        # to a value between 0 and 40 for easier handling by the visualizaton. 
        energy = clamp(ShortTermFeatures.energy(signal) / 100, 0.0, 40.0)

        # Convert raw frequency data to numeric value that can be used in our visualization logic
        frequency = (F[0] * 10)[0]

        # Build sound data struct of energy and frequency
        sound_data = {
            'energy': energy,
            'frequency': frequency,
        }
   
        # Send sound data struct to queue to be handled by visualizer processes
        sound_data_queue.put(sound_data)


# Function to initialize our VisPy Canvas class and start the VisPy app
def start_visualization(sound_data_queue):
        c = Canvas(sound_data_queue)
        app.run()


if __name__ == '__main__':
    # Get user args and options
    opts, args = getopt.getopt(sys.argv[1:], "Hrh:w:", ["help", "reset", "height=", "width="])

    # Save default settings before reading from file if reset arg passed
    for opt, arg in opts:
        if opt in ("-H", "--help"):
            print(
                """
                Usage: python3 audio_nebula.py <args>
                    -H/--help -----------------------------> Usage tips
                    -r/--reset ----------------------------> Reset to default settings
                    -h/--height <positive integer> --------> Height of visualizer window in pixels
                    -w/--width <positive integer> ---------> Width of visualizer window in pixels
                """
            )
            sys.exit(0)
        if opt in ("-r", "--reset"):
            save_settings()

    # Load settings from YAML file
    read_settings()

    for opt, arg in opts:
        if opt in ("-w", "--width"):
            try:
                if int(arg) > 0:
                    set_setting('width', int(arg))
                else:
                    print("Width argument must be greater than 0")
                    sys.exit(2)
            except ValueError:
                print("Width argument must be a positive integer greater than 0")
                sys.exit(2)

        elif opt in ("-h", "--height"):
            try:
                if int(arg) > 0:
                    set_setting('height', int(arg))
                else:
                    print("Height argument must be greater than 0")
                    sys.exit(2)
            except ValueError:
                print("Height argument must be a positive integer greater than 0")
                sys.exit(2)

    # Initialize queue for passing sound data
    sound_data_queue = Queue()

    # Initialize visualization process
    viz_process = Process(target = start_visualization, args = ([sound_data_queue]))

    # Initialize audio processing process
    audio_process = Process(target = start_recording, args = ([sound_data_queue]))

    # Start both processes
    viz_process.start()
    audio_process.start()

    # Keep audio process open as long as visualization process remains open
    viz_process.join()
    sound_data_queue.close()
    audio_process.terminate()