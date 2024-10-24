# yesican
Python code to read CAN bus information from a BMW 116i.

## Objective
The initial objective is to add a display to my dashboard that helps me get very close the the pit speed limit without exceeding it, hence minimising my pit stop times.  It would be good to develop this to a full pit speed limiter, perhaps by interacting with the rev limiter or cutting fuel injection, but that may not be possible.

The second objective is to add a gear shift indicator.

A third possibility is to add a range indicator but quoting the range in laps and time, as these are the values that matter to me during a race; particularly time range.

## Intended Platform
Raspberry Pi II running in a BMW 116i E87, connected to its CAN bus using a Korlan USB2CAN adapter.

## Design Considerations
If we only needed a speed limiter and a shift indicator, a row of LEDs would be suitable, with a two way switch to change modes (speed limiter / gear shift) and a push button to cycle around pit speed limits.  However, a display would be much more flexible.  Although repurposing a phone for the display is attractive, this would increase the complexity of the solution.  Also, Motorsports UK regulations specify that we may not carry a phone in the car.

Therefore, I think the components of the system will be:

* Raspberry Pi with SD for RAM
* Memory stick for its HD
* Korlan USB2CAN adapter with DB9 cable
* DB9 socket wired into the P-CAN (100 kbps)
* Display
* Cigarette lighter to USB adapter and cable to connect into the Pi
