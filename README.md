### Cycle UI

![alt text](https://github.com/imbadatgit/cycleUI/blob/master/doc/ui-cut.png "UI features")

Cycle UI is a desktop tool to read out and visualize the data from a
stationary bicycle. This way, you can place a laptop over the
bicycle computer and yet be able to monitor your progress. The
connection to the bicycle is established with a [Digispark
microcontroller](http://digistump.com/products/1).


## Features

So far, the UI features the following basic functionality, displaying

* _active ride time_, i.e., time spent on the bicycle during which the wheels were actually turning,
* _speed_, which is really just a guesstimate calculated from
* _revelations per minute_,
* and the _total number of revelations_.

In addition, speed is plotted on a graph to keep me motivated. Here's a
quick screenshot of the UI in action, shown above a random YouTube
cycling video:

![alt text](https://github.com/imbadatgit/cycleUI/blob/master/doc/in-action.png "UI in action")

The overlay stays on top and is quite unintrusive. 

## Requirements

Python

* pySerial (tested with version 2.6)

For the microcontroller

* Digispark or some other Arduino-like board
* 3.5mm stereo audio jack
* 10K ohm resistor (for pulldown)

In addition, you need to install some of the ["DSEG"](http://www.keshikan.net/fonts-e.html) fonts.

## How to run
Upload the cycle.ino sketch onto a Digispark. Any other Arduino will also work with slight modifications to the serial commands.

Then connect the Digispark to your computer (via the primary USB port) and start the UI:

    python ui.py

Depending on your OS settings, you may have to change USB permissions for this to work.

## Wiring 

Somewhere inside the bicycle, a switch closes at a fixed point during
each revolution.  My bicycle (of the renowned
["Ultrasport"](http://ultrasport.net/) brand) has a 3.5mm stereo
headphone jack connecting the bicycle internals to the stock
computer. Unfortunately, the switch does not make use of the ground wire
but instead connects to the left and right channel.

I simply connected these to the pin #2 and 5v on the Digispark. I
further added a pulldown resistor between pin #2 and ground. The
Digispark counts revolutions and measures the time between, from which
the UI calculates speed and distance. 

![alt text](https://github.com/imbadatgit/cycleUI/blob/master/doc/cycle_bb.png "Digispark cycling controller schematics")
