# BLEScanner - TODO

## NEW: Rescan Sensor
Rescan if no data for the sensor (happens if sensor not found).
### Status
Not started.

## NEW: Pretty Output
Option to show the output in JSON pretty format with CRLF and TAB indent.
### Status
Not started.

## NEW: Scan Multiple Times
Option to scan for data multiple times with delay between the scans.
### Status
Not started.

## NEW: Domoticz Hardware Controller Plugin
Create a single Domoticz hardware controller plugin for multiple BLE sensors.
Same concept as for the hardware controller dummy with the option to create devices.
Use a dialog to a add a new device with sensor type (Govee5075, ATCMiThermometer), name and MAC address (NN:NN:NN:NN:NN:NN).
The data for the device (sensor) to be gathered using the BLE Scanner (blescanner.py) as external subprocess.

**Note:**A simpler solution is to create a plugin per sensor type, like Govee5075, ATCMiThermometer but that would mean a lot
of hardware controllers. Each sensor has its own hardware controller.
### Status
Not started.
