# Audio Nebula Design

## Initial Goals
My primary goal going into this project was to develop an audio visualizer that looked unique to anything I had seen before, and that was fast and responsive enough that the visualization truly felt like a representation of the audio in realtime. I knew something that looked bland or that was very slugglish and operated on a big delay or with frequent crashes would not lend itself to an engaging experience, so these two goals stood out to me as what would lead to a successful project.

As a secondary goal, I wanted to introduce some customization options that would lay the foundation for a direction for the project to continue to grow and develop as I work on it beyond CS50.

## Research
At the onset of development on this project, I researched a number of Python libraries that would support my primary goal to process audio and create a visually appealing visualization, and do both things efficiently enough that the effect of it happening in realtime would feel seamless.

PyAudio seemed to be a very common and standard option as far as streaming audio from a mic input goes. Getting that up and running (first set only to record a brief 10 second audio clip, and later to infinitely stream audio data for the duration of the program's runtime), was fairly straightforward and it was immediately clear that it would do what I needed it to do.

pyAudioAnalysis was another library I found of particular interest, in that it offered a lot of options to take raw audio data and pull useful information from it, including energy and frequency values. I knew getting raw audio condensed to a few key data points would be a must to make my ultimate visualization meaningful, and this libary gave me the flexibility to calculate the data I needed without wasting resources computing anything I didn't.

Finally, VisPy was the library I ultimately decided to use for my visualization layer. I did explore a few other options, but found that they tended to lend themselves better to data science applications, and I wasn't immediately drawn to the visuals from a creative standpoint. VisPy uses OpenGL to render graphics using the GPU, which seemed to open up a lot of doors to really customizing a visual component to the program that is memorable and unique.

## Primary Implementation
Once I'd settled on my libraries and felt comfortable with how to use each piece in isolation, it was time to bring it all together to meet the gaols I'd set for the project.

The program currently works as a command line interface tool that can be executed via the terminal. Once it starts up, two distinct processes spin up, and a queue is initialized to share data between them. In one process, PyAudio begins to stream audio data from the users' mic, processing each chunk of audio data via pyAudioAnalysis to extract useful information and store it in a data struct. This audio data is then passed into the queue before the process loops to handle the next chunk of incoming audio.

Meanwhile, a second process is spun up that initializes a visualization canvas class to render a point cloud visualization. The OpenGL shader code comes from an example provided by the library's authors, but the Python layer has been customized to look and behave according to how I wanted the ultimate visualization to look. This visualization is initialized with a timer event that modifies any visualization data needed (color, movement, zoom, etc.) and loads a new frame of the visualization based on this data.

In this timer event, I set up the visualization to pull audio data out of the queue that had been sent by the other process, and use this data to drive how the visualization data changes. For example, energy data is used to affect particle color and speed, while frequency is used to affect particle size. The effect of this is that each time the visualization reloads, it does so according to the latest audio data, creating realtime feedback where a user can see the visualization change based on the audio they input.

## Settings Implementation
Once I had the central visualization loop working as I wanted, I began work on my secondary goal of allowing a degree of user customization via settings. The visualization canvas supported interactivity, which allowed me to support key strokes to trigger certain behavior. I implemented an option to swap color palettes, as well as one to adjust microphone sensitivity (by applying a multiplier across all calculations involving audio energy). I also added some flags to the cli to allow users to enter custom window dimensions for the visualization canvas.

Once this was working, I wanted a way to save these settings, as well as the option to revert to defaults. To do this, I implemented a system based on a local YAML file that the program reads into memory. As users change settings while the program is running, these settings in memory are modified and then saved to the YAML file. If a user chooses to reset to defaults via a cli flag, their settings file is overwritten by one containing the default settings hard coded into a utils file for setting management.

All of this lays the foundations for what can become a much more robust settings system as the project continues to develop and new customization options are added, including eventual support for custom settings presets that can be switched between as desired.

## Challenges
The most substantial design challenge I encountered in this project was the multiprocessing queueing system I had to devise in order to make things work. My initial instinct was to just run everything in a single process, first starting up the visualization class, then starting the audio processing loop. This of course did not work, because there was no ability for the visualization to update while the audio was streaming. Both of these things require constant action, and I found that I could make the visualization run, OR I could make the audio stream, but trying to do both at once would not produce the desired effect.

I eventually realized that this was a textbook example of why multiprocessing exists, so I did some further research into how to set up processes and use a queue to pass data between them. Sure enough, this allowed the visualizer to run as I'd initially intended, and in the process created much cleaner and more well-designed code. Breaking one large problem into two smaller ones allowed me to address a technical limitation but also a creative one by allowing me to better conceptualize each process in isolation and made for a much more successful project.