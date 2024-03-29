# BLEScanner - README

The BLE Scanner is a tool to scan for Bluetooth Low Energy (BLE) devices and return a JSON object (array) holding the list of devices found with address, name and optional advertised data.

## Requirements
* Python version 3
* [Bleak](https://github.com/hbldh/bleak)

Tested with Python 3.11.4 and Bleak 0.20.2.

## Run
```
python3 blescanner.py arguments
```
**Arguments**
| Argument | Brief   | Values      | Description                                                         |
| ---------|:-------:|:------------| ------------------------------------------------------------------- |
| -m       | mac     | MAC address | MAC address for single device only                                  | 
| -t       | timeout | Seconds     | Scanning duration in seconds. Default 10 seconds. Minimum 5 seconds |
| -a       | advdata | 0=Off, 1=On | Add advertised data to the result                                   | 
| -d       | debug   | 0=Off, 1=On | Debug information                                                   | 

## Examples running BLEScanner from Command Line
**Scan for all BLE devices**

Get advertised data for all BLE devices found during a 5 seconds scan.
```
python3 blescanner.py -t 5 -a 1
```
**Output**
```
[
{"address": "70:2A:D5:7E:23:26", "name": null, "advertisementdata": {"manufacturer_data": true, "0X75": "4204018060702AD57E2326722AD57E232501000000000000", "rssi": -90}}, 
{"address": "A4:C1:38:52:74:C2", "name": "ATC_5274C2", "local_name": "ATC_5274C2", "advertisementdata": {"service_data": true, "0000181A-0000-1000-8000-00805F9B34FB": "C2745238C1A4A406F81759091B410E", "rssi": -46}}, 
{"address": "F7:6F:D8:27:B7:8D", "name": "Ruuvi B78D", "local_name": "Ruuvi B78D", "advertisementdata": {"manufacturer_data": true, "0X499": "050D255DB8CAFEFFE4006C03F8AB761CAFC6F76FD827B78D", "rssi": -59}}, 
{"address": "76:73:5D:F9:74:96", "name": null, "advertisementdata": {"service_data": true, "0000FEF3-0000-1000-8000-00805F9B34FB": "4A17234D52584A1132D1308AC746ECB6A1393FF8102BFDAB6BC685", "rssi": -63}}, 
{"address": "A4:C1:38:38:A9:0C", "name": "ATC_38A90C", "local_name": "ATC_38A90C", "advertisementdata": {"service_data": true, "0000181A-0000-1000-8000-00805F9B34FB": "0CA93838C1A48C068017270B5DA40E", "rssi": -52}}
]
```

**Scan for single device** 

Get advertised data for single device during a 5 seconds scan.
```
python3 blescanner.py -t 5 -a 1 -m 28:CD:C1:09:05:98
```
**Output**
```
[
{"address": "28:CD:C1:09:05:98", "name": "PICOW", "local_name": "PICOW", "advertisementdata": {"manufacturer_data": true, "0X4C52": "32383930", "rssi": -74}}
]
```

## Examples running BLEScanner from Python script
See folder **examples** for some scripts ruuning the BLE Scanner to get device data.

The sensor examples, like the Govee GVH5075, Xiaomi Mi TempHum, Ruuvi RuuviTag, include decoding sensor data into properties temperature, humidity, battery level and more.

In addition, there are **Automation Event** examples, written in **dzVents**, for the **Domoticz Home Automation System**.
The examples run the BLE Scanner for a given sensor MAC address and decode the sensor data from the JSON object returned by the BLE Scanner.
The decoded sensor data is used to update a Domoticz Virtual Sensor (Domoticz hardware controller Dummy), like a Temp + Humidity device.

## Licence
This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS for A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with the samples.  If not, see [GNU Licenses](http://www.gnu.org/licenses/).
