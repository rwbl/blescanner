#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
File: blescanner_ruuvitag.py
Date: 20240105
Author: Robert W.B. Linn
Scan for a single BLE device Ruuvi RuuviTag (ruuvitag) and decode the data published.
Dependencies: blescanner.py - Tool to scan for Bluetooth Low Energy (BLE) devices.

The RuuviTag is a wireless Bluetooth sensor node that measures temperature, air humidity, air pressure and movement.

Company: Ruuvi Innovations Ltd. (1177)
Name (complete): Ruuvi B78D
Nordic UART Service

Sensor Log Data:
Reading the sensor log data is not used.

Dataformat:
Advertised Data (ADV)
The advertised data is a dict with one entry. 
Advertised data is 24 bytes: data (18) + macaddress (6)
Example:
Key=0X499 Value=050C7A5E64C7FFFFE8006C03FCAA9619319EF76FD827B78D
The advertised characteristics data received has 18 bytes, like 050C7A5E64C7FFFFE8006C03FCAA9619319E:
The dataformat 05 (RAWv2, ID: 0x05) is used. Reference: https://github.com/ruuvi/ruuvi-sensor-protocols

Offset  | Allowed values        | Description
-------	|:---------------------:|-----------
0       | 5                     | Data format (8bit)
1-2     | -32767 ... 32767      | Temperature in 0.005 degrees
3-4     | 0 ... 40 000          | Humidity (16bit unsigned) in 0.0025% (0-163.83% range, though realistically 0-100%)
5-6     | 0 ... 65534           | Pressure (16bit unsigned) in 1 Pa units, with offset of -50 000 Pa
7-8     | -32767 ... 32767      | Acceleration-X (Most Significant Byte first)
9-10    | -32767 ... 32767      | Acceleration-Y (Most Significant Byte first)
11-12   | -32767 ... 32767      | Acceleration-Z (Most Significant Byte first)
13-14   | 0 ... 2046, 0 ... 30  | Power info (11+5bit unsigned), first 11 bits Is the battery voltage above 1.6V, in millivolts (1.6V To 3.646V range). Last 5 bits unsigned are the TX Power above -40dBm, in 2dBm steps. (-40dBm To +20dBm range)
15      | 0 ... 254             | Movement counter (8 Bit unsigned), incremented by motion detection interrupts from accelerometer
16-17   | 0 ... 65534           | Measurement sequence number (16 Bit unsigned), each time a measurement is taken, this is incremented by one, used for measurement de-duplication. Depending on the transmit interval, multiple packets with the same measurements can be sent, And there may be measurements that never were sent.
18-23   | Any valid mac         | 48bit MAC address. THIS IS NOT USED as does not fit into the message length.

Data Example
HEX:
050B856030C879FFE0006403F8AA16193843
Data:
{"mac": "F7:6F:D8:27:B7:8D", "name": "Ruuvi B78D", "status": "OK", "message": "", "temperature": 14.71, "humidity": 61.54, "airpressure": 1013.2, "accelerationx": -32, "accelerationy": 108, "accelerationz": 1016, "voltage": 2.9606875, "batterylevel": "19.550342130987293", "txstrength": 4, "movementcounter": 25, "sequencecounter": 14407}
"""

import subprocess
import json
from typing import Dict
import struct

# Debug flag 0 (OFF), 1(ON)
_DEBUG = 0

# Timeout of the subprocess running the blescanner.py.
# The value must be > parameter mode 1 timeout used by the blescanner.py.
_TIME_OUT_SUBPROCESS = 30

# Timeout running the ble scanner.
_TIME_OUT = 10

# Advertised data
_ADVDATA = 1

# Single device MAC address
_MAC = "F7:6F:D8:27:B7:8D"

# BLE handler External Python script
# The Domoticz parameter homefolder is used to set the path = see onstart
_BLE_HANDLER = "blescanner.py"
_PYTHON_COMMAND = "python"
_BLESCANNER = "blescanner.py"

# DeviceSpecifics
# Data contains 6 bytes
_ADDRESS_KEY = "address"
_NAME_KEY = "name"
_ADVERTISEMENT_KEY = "advertisementdata"
# Manufacturer key used from the advertisementdata
_MANUFACTURER_KEY = "0X499"

# Manufacturer data received data dict length (single entry only)
_MANUFACTURER_DATA_LENGTH = 1

# Advertised data length = date(18 bytes) + macaddress(6 bytes)
_ADVERTISED_DATA_LENGTH = 24

# Header datatype for advertisement data, do _not_ change
_DATATYPE_ADV = 0x05

# Battery levels between min 1.6V - max 3.646V
_BATTERY_LEVEL_MIN = 1.600
_BATTERY_LEVEL_MAX = 3.646

################################################################################
# DECODE DATA
################################################################################

def decode_data(data):
    """Decode the data (6 bytes) into a json object with properties."""
    
    # _DEBUG = 1
    if _DEBUG:
        # {'mac': 'F7:6F:D8:27:B7:8D', 'name': 'Ruuvi B78D', 'status': 'OK', 'message': '', 'temperature': 15.5, 'humidity': 63, 'airpressure': 1002, 'accelerationx': 64, 'accelerationy': 28, 'accelerationz': 1032, 'voltage': 3.01, 'batterylevel': 68, 'txstrength': 4, 'movementcounter': 6, 'sequencecounter': 194}
        print(f"[DEBUG decode_data]{data}")

    # Get the macaddress and the device name.
    macaddress = data[_ADDRESS_KEY]
    name = data[_NAME_KEY]

    # Get the data from manufacturer key and convert from string to hex
    data = bytes.fromhex(data[_ADVERTISEMENT_KEY][_MANUFACTURER_KEY])

    if _DEBUG:
        print(f"[DEBUG decode_data] {data.hex().upper()}")

    # Use Dict from typing to create a dict with str, float, int values
    result: Dict[str, object] = {}

    # Check the length of the data = must be 6 bytes
    if len(data) != _ADVERTISED_DATA_LENGTH:
        msg = f'Received wrong data size (bytes). Expect {_ADVERTISED_DATA_LENGTH}, received {len(data)}'
        result = {
            "mac": macaddress,
            "name": name,
            "status": "ERR",
            "message": msg
        }
    else:
        
        # Get the first 18 bytes from the data.
        # The 6-byte mac address 19-24 is not used.
        data = data[0:18]

        # Handle data received and select type ADV
        # Get the data if the datacounter is 1 and then stop reading adv data
        if data[0] == _DATATYPE_ADV:

            # Unpack the bytearray data 18 bytes into tuple 10 items
            # >=big indian, h=short (2 bytes), B=unsigned char (1 byte), H=unsigned short (2 bytes)
            # 1 + 2 + 2 + 2 + 2 + 2 + 2 + 2 + 1 + 2 = total 18 bytes
            dat = struct.unpack('>BhHHhhhHBH', data)
            v = round(((dat[7]/32)+1600)/1000.0,2)

            # Create the dict and assign the data to the properties
            result = {
                "mac": macaddress,
                "name": name,
                "status": "OK",
                "message": "",
                "temperature": round(dat[1]/200.0,1),           #°C
                "humidity": int(dat[2] / 400.0),                #%RH
                "airpressure": int((dat[3] + 50000) /100.0),    #mBar or hPa
                "accelerationx": dat[4],                        #
                "accelerationy": dat[5],                        #
                "accelerationz": dat[6],                        #
                "voltage": v,                                   #V
                "batterylevel": int( (v - _BATTERY_LEVEL_MIN) / (_BATTERY_LEVEL_MAX - _BATTERY_LEVEL_MIN) * 100 ),
                "txstrength": (dat[7] % 32) * 2 - 40,           #dBm
                "movementcounter": dat[8],                      #Number
                "sequencecounter": dat[9]                       #Number
            }
        else:
            result = {"mac":macaddress,"status":"ERR", "message":"Received wrong data type."}
            
        if _DEBUG:
            print(f"[DEBUG decode_data]{result}")

    # Return the dict (JSON object)
    return result

################################################################################
# BLE SCANNER
################################################################################
            
def ble_scanner(mac, timeout, advdata, debug):
    """Scan for BLE devices and send to the Domoticz log"""

    try:
        if debug:
            print(f'[DEBUG ble_scanner] called {mac}')
        
        # The external script must located in the same folder as the plugin
        # Command executed: python3 blescanner.py timeout advertised_data
        # Data returned from external script as encoded bytes
        data = subprocess.check_output(
            [
                _PYTHON_COMMAND,
                _BLESCANNER,
                '-m ' + mac,
                '-t ' + str(timeout),
                '-a ' + str(advdata),
                '-d ' + str(debug)
            ],
            shell = False, 
            timeout = _TIME_OUT_SUBPROCESS,
            stderr = subprocess.STDOUT)

        # Data received from external script
        # Decode the data from b'{"key...' to a data string
        datastr = str(data.decode('utf8')).strip()
        if debug:
            print(f'[ble_scanner] completed={datastr!r}')
        # Parse the data string containing the json array with devices
        devices_found = json.loads(datastr)
        # Check if there are devices
        if len(devices_found) > 0:
            return True, devices_found
        else:
            return False, None
        
    except subprocess.CalledProcessError as err:
        print(f'[ERROR ble_scanner] CalledProcess returncode={err.returncode}, output={err.stdout},{err.stderr}')
        return False, None

    except subprocess.TimeoutExpired as err:
        print(f'[ERROR ble_scanner] Reached timeout {err.cmd}s.')
        return False, None

################################################################################
# MAIN
################################################################################

if __name__ == "__main__":
    print(f'Scanning single device {_MAC} for {_TIME_OUT} seconds.')

    # Scan for single device using its MAC address
    status, devices = ble_scanner(_MAC, _TIME_OUT, _ADVDATA, _DEBUG)

    # Handle the ble scanner result
    # The json array should contain a single entry (index 0)
    if status:
        if len(devices) == 1:
            if _DEBUG:
                print(devices['address'], devices['name'], devices['advertisementdata'])
            devdata = decode_data(devices[0])
            # {'mac': 'F7:6F:D8:27:B7:8D', 'name': 'Ruuvi B78D', 'status': 'OK', 'message': '', 'temperature': 15.5, 'humidity': 63, 'airpressure': 1002, 'accelerationx': 64, 'accelerationy': 28, 'accelerationz': 1032, 'voltage': 3.01, 'batterylevel': 68, 'txstrength': 4, 'movementcounter': 6, 'sequencecounter': 194}
            print(devdata)
    else:
        print(f'[WARNING] Device {_MAC} not found.')

