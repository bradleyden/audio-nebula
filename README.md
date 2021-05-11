# Audio Nebula
An astronomy-inspired audio visualizer written in Python

## Introduction
Audio Nebula is an audio visualizer that reads input from the microphone and renders a visualization in realtime based on the user's audio input. A particle cloud is used to create a visual reminiscent of a swirling galaxy or nebula cloud that reacts to sound.

Audio energy (amplitude) is used to affect the color and movement speed of particles.

Frequency is used to affect the size and opacity of particles.

## Setup Guide
Clone this repository to your local machine with a Python 3 development environment. This project relies on a GPU-driven visual output, so it may not work in an IDE or another virtual Python environment.

* `cd` into the project directory and run the following:
* Ensure `portaudio` is installed on your system using your preferred package manager (`brew`, `apt`, etc.)
    * `brew install portaudio` works for Mac
    * `sudo apt install libasound-dev` works for Ubuntu
* Run `pip3 install -r requirements.txt`
* Run `pip3 install -r ./src/pyaudioanalysis/requirements.txt`

Depending on your system configuration, some dependencies may need to be installed individually in order to get the program to run. 

Run the program with `python3 audio-nebula.py`

Optionally, the following flags can be used when running the program:
* -h, --height -> Set the visualization window height, in pixels. Must be followed by an integer greater than 0.
* -w, --width -> Set the visualization window width, in pixels. Must be followed by an integer greater than 0.
* -r, --reset -> Reset all settings to program defaults. This flag takes no further input.

Program settings will be saved to a file called `settings.yml`, and if this file is missing or invalid, program defaults will be used and saved automatically when the program is run.

## User Guide
While the program is running, you should immediately notice that the visualization is responding to your connected mic input.

A few controls can be used while the visualization is running to customize how it looks and behaves. Adjusting these settings will automatically save them so that they will be retained next time you run the program, until you explicitly reset defaults.

* `o`: Decrease microphone sensitivity
* `p`: Increase microphone sensitivity
* `c`: Toggle color scheme

To end the visualization and quit the program, hit `q`, `esc`, or just close the visualizaiton window.





