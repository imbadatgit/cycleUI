### Cycle UI

Cycle UI is a tool to read out and visualize the data from a stationary
bicycle. This way, you (i.e., I) can place a laptop over the bicycle
computer and yet be able to monitor your progress. The connection to the
bicycle is established with a [Digispark
microcontroller](http://digistump.com/products/1).

## Features

So far, the UI features basic functionality. It displays 

* _active ride time_, i.e., time spent on the bicycle during which the wheels were actually turning,
* _speed_, which is really just a guesstimate calculated from
* _revelations per minute_,
* and _total number of revelations_.

Here's a quick screenshot of the UI in action, shown above a random YouTube cycling video:

![alt text](http:// "UI in action")

The overlay stays on top and is quite unintrusive. 

## How to run
Upload the cycle.ino sketch onto a Digispark. Any other Arduino will also work with slight modifications to the serial commands.

Then connect the Digispark to your computer and start the ui:

    python ui.py

## Wiring 

Somewhere inside the bicycle, a switch closes at a fixed point during
each revolution.  My bicycle (of the renowned
["Ultrasport"](http://ultrasport.net/) brand) has a 3.5mm stereo
headphone jack connecting the bicycle internals to the stock
computer. Unfortunately, the switch does not make use of the ground wire
but instead connects to the left and right channel.

I simply connected these to the pin #2 and 5v on the Digispark. I
further added a pulldown resistor between pin #2 and ground. The
Digispark then counts revolutions and measures the time between them to
calculate speed, distance, and potentially other useful stats (not
implemented).

