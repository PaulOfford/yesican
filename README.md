# yesican
## Introduction
This app provides club racers with three bits of useful information:

* Pit Speed Indicator - like a speedometer but focused on enabling you
to use every kph of a pit speed limit
* Gear Shift Indicator - a set of lights that make sure you take
your car right up to the red line but no further
* Brake Trace - a real time plot showing brake pressure and throttle
position to perfect your trail braking and heel & toe downshifts

The software can be used with any computer operating system that
has a graphical interface and supports Python.  It's been successfully
run on:

* Windows 10 or 11
* Raspberry Pi Raspbian, Bookworm and Bullseye

## Supported Cars

The app currently only supports the BMW E87.  It may work with other
E8x models.  Adding support for other cars is fairly straightforward;
it just requires editing of the code in can_interface.py to test for
the appropriate CAN bus aribitration IDs (CAN IDs) and byte positions.

## Installation
You can install the software by downloading a zip file or by cloning a
Git repository.

### From a zip file
* Go to https://github.com/PaulOfford/yesican
* Click on the green Code button
* Choose Download ZIP
* Extract the zip file to a folder of your choice
  * The folder must allow write access as config updates are stored there

### From a git repository
* Open a Command Prompt on your Windows PC, or a Terminal on your
Raspberry Pi / Ubuntu / Debian machine
* Check that you have git installed by entering the command: `git`
* Use cd/chdir to navigate to a folder of your choice
* Enter the command: `git clone https://github.com/PaulOfford/yesican.git`
* This will create a new subdirectory called `yesican`

A more complete set of instructions can be found
at https://pauloffordracing.com/gear-shift-and-pit-speed-indicator/

## Running the App

From a command or terminal prompt, change to the `yesican` directory,
and enter: `python -m yesican`

## Frequently Asked Questions

#### How can I run the software with test data?
* Make a backup copy of the config.ini file.
* Edit the config.ini file with a text editor like Notepad, nano or gedit.
* In the `[general]` section change the line `test_mode = false`
to `test_mode = true`
  * NB: lines in the config.ini file are case-sensitive, i.e.
  `test_mode = True` will not work

#### How can I stop the app running in fullscreen mode?
* Make a backup copy of the config.ini file.
* Edit the config.ini file with a text editor like Notepad, nano or gedit.
* In the `[general]` section change the line `fullscreen = true`
to `fullscreen = false`

## Known Bugs
None at this time.
