# Audio Nebula
An astronomy-inspired audio visualizer written in Python

![AudioNebula](https://user-images.githubusercontent.com/28875814/117913204-f5091980-b2ae-11eb-8cdd-fb3eec726d51.png)

## Introduction
Audio Nebula is an audio visualizer that reads input from the microphone and renders a visualization in realtime based on the user's audio input. A particle cloud is used to create a visual reminiscent of a swirling galaxy or nebula cloud that reacts to sound.

Audio energy (amplitude) is used to affect the color and movement speed of particles.

Frequency is used to affect the size and opacity of particles.

Video walkthrough can be viewed here: https://www.youtube.com/watch?v=242zK0Id2nQ

## Setup Guide
Clone this repository to your local machine with a Python 3 development environment. This project relies on a GPU-driven visual output, so it may not work in an IDE or another virtual Python environment.

* `cd` into the project directory and run the following:
* Ensure `portaudio` is installed on your system using your preferred package manager (`brew`, `apt`, etc.)
    * `brew install portaudio` works for Mac with homebrew installed
    * `sudo apt install libasound-dev` works for Linux systems using the apt package manager
* Run `pip3 install -r requirements.txt`
* Run `pip3 install -r ./src/pyaudioanalysis/requirements.txt`

Depending on your system configuration, some dependencies may need to be installed individually if installing via the requirements files does not work. This program was developed and primarily tested on a Kubuntu system running Python 3.8.6. I did verify that it will run on Mac as well, but visuals and performance may differ.

Your system must have a microphone connected as the primary audio input for the program to behave as intended.

Run the program with `python3 audio-nebula.py`

Optionally, the following flags can be used when running the program:
* -H, --help -----> Get help about program usage. This flag takes no further input.
* -h, --height ---> Set the visualization window height, in pixels. Must be followed by an integer greater than 0.
* -w, --width ----> Set the visualization window width, in pixels. Must be followed by an integer greater than 0.
* -r, --reset ----> Reset all settings to program defaults. This flag takes no further input.

## Settings
Program settings will be saved to a file called `settings.yml`, and if this file is missing or invalid, program defaults will be used and saved automatically when the program is run.

Settings will be saved automatically as they are adjusted. Adjusting the color scheme, mic sensitivity, or application window dimensions (via command line arguments only) will all be preserved between uses.

All of these settings can be reset at any time by passing the `--reset` flag when launching the program.

## User Guide
When the program starts, a new window should appear displaying a point cloud graphic output. You should immediately notice that the visualization is responding to your connected mic input.

A few controls can be used while the visualization is running to customize how it looks and behaves. As mentioned above, adjusting these settings will automatically save them so that they will be retained next time you run the program, until you explicitly reset defaults.

* `o`: Decrease microphone sensitivity. This will affect any visualiztion feature driven by audio energy.
* `p`: Increase microphone sensitivity. This will affect any visualiztion feature driven by audio energy.
* `c`: Toggle color scheme

To end the visualization and quit the program, hit `q`, `esc`, or just close the visualizaiton window.

## Further Reading
* [PyAudio](https://github.com/jleb/pyaudio)
* [pyAudioAnalysis](https://github.com/tyiannak/pyAudioAnalysis)
* [VisPy](https://github.com/vispy/vispy)





