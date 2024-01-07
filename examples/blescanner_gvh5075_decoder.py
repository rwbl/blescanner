#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
File: blescanner_gvh5075_decoder.py
Date: 20240106
Author: Robert W.B. Linn
Scan for a single BLE device Govee 5075 (gvh5075_1757) and decode the data published.
Dependencies: blescanner.py - Tool to scan for Bluetooth Low Energy (BLE) devices.

The GVH5075 is a wireless Bluetooth Low Energy (BLE) sensor node that sends current readings temperature & humidity & battery health every 2 seconds.

Dataformat:
The advertised data is a dict with two entries.
The entry with 2-bytes-uuid key 0xEC88 is used (Manufacturer Key).
The data has 6 bytes.
Example: key=0XEC88, data=00029E436400
Data Conversion:
data (6 bytes)=00029E436400 > 00 02 9E 43 64 00
The temp+hum are calculated from the first 4 bytes:
The data bytes 0-4 = HEX 00 02 9E 43 > converted to DEC 171587
temperature = 171587 / 10000 = 17.1 °C              (round, 1)
humidity    = 171587 % 1000 = 587 / 10 = 58.7 %RH   (int)
battery     = data byte 5 = 64 > DEC 100            (int)
Result:
{"mac": "A4:C1:38:D1:17:57", "name": "GVH5075_1757", "status": "OK", "message": "", "temperature": 17.1, "humidity": 58, "batterylevel": 100}
"""

import argparse
import os
import subprocess
import json
from typing import Dict
import struct

# Debug flag 0 (OFF), 1(ON)
_DEBUG = 0

# Timeout of the subprocess running the blescanner.py.
# The value must be > parameter mode 1 timeout used by the blescanner.py.
_TIMEOUT_SUBPROCESS = 30

# Timeout running the ble scanner.
_TIMEOUT = 10

# Advertised data
_ADVDATA = 1

# Working dir - use for Domoticz only to set the working directory scripts/python/ as argument
# Ensure to end with /
_WORKING_DIR = ""

# Single device MAC address
_MAC = "A4:C1:38:D1:17:57"

# BLE handler External Python script
_BLE_HANDLER = "blescanner.py"
_PYTHON_COMMAND = "python"
_BLESCANNER = "blescanner.py"

# GVH Specifics
# Data contains 6 bytes
_ADVERTISED_DATA_LENGTH = 6
_ADDRESS_KEY = "address"
_NAME_KEY = "name"
_ADVERTISEMENT_KEY = "advertisementdata"
# Manufacturer key used from the advertisementdata
_MANUFACTURER_KEY = "0XEC88"

################################################################################
# DECODE DATA
################################################################################

def decode_data(data):
    """Decode the data (6 bytes) into a json object with properties."""
    
    # _DEBUG = 1
    if _DEBUG:
        # {'address': 'A4:C1:38:D1:17:57', 'name': 'GVH5075_1757', 'local_name': 'GVH5075_1757', 'advertisementdata': {'manufacturer_data': True, '0XEC88': '000286C15F00', '0X4C': '0215494E54454C4C495F524F434B535F48575075F2FF0C', 'rssi': -60}}
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
        
        # Get the first 4 bytes holding the temp + hum data
        # Example 00 02 6B 8E 64 00 > 00 02 6B 8E
        temphumdata = data[0:4]

        # Unpack packed value into original representation with specified format.
        # There is a single entry in the tuple; > = big-endian, I = unsigned int
        raw = struct.unpack(">I", temphumdata)[0]
        if raw & 0x800000:
            is_negative = True
            raw = raw ^ 0x800000
        else:
            is_negative = False

        temperature = int(raw / 1000) / 10
        if is_negative:
            temperature = 0 - temperature

        humidity = (raw % 1000) / 10

        # Get the battery from byte 4
        # Example 00 02 6B 8E 64 00 > 64 > DEC 100
        raw = data[4]
        batterylevel = raw

        # Create the dict and assign the data to the properties
        result = {
            "mac": macaddress,
            "name": name,
            "status": "OK",
            "message": "",
            "temperature": round(temperature,1),
            "humidity": int(humidity),
            "batterylevel": int(batterylevel)
        }

        if _DEBUG:
            print(f"[DEBUG decode_data]{result}")

    # Return the dict (JSON object)
    return result

################################################################################
# BLE SCANNER
################################################################################
            
def ble_scanner(mac, timeout, advdata, workingdir, debug):
    """Scan for BLE devices and send to the Domoticz log"""

    try:
        if debug:
            print(f'[DEBUG ble_scanner] called {mac}, {os. getcwd()}')
        
        # The external script must located in the same folder as the plugin
        # Command executed: python3 blescanner.py timeout advertised_data
        # Data returned from external script as encoded bytes
        data = subprocess.check_output(
            [
                _PYTHON_COMMAND,
                workingdir + _BLESCANNER,
                '-m ' + mac,
                '-t ' + str(timeout),
                '-a ' + str(advdata),
                '-d ' + str(debug)
            ],
            shell = False, 
            timeout = _TIMEOUT_SUBPROCESS,
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
    # print(f'Scanning single device {_MAC} for {_TIMEOUT} seconds.')

    # python3 blescanner.py -t 5 -a 1 -m 28:CD:C1:09:05:98
    parser = argparse.ArgumentParser()        
    parser.add_argument("-m", "--mac", default=_MAC, type=str)    
    parser.add_argument("-w", "--workingdir", default=_WORKING_DIR, type=str)    
    parser.add_argument("-t", "--timeout", default=_TIMEOUT, type=int)    
    parser.add_argument("-d", "--debug", default=_DEBUG, type=int)    

    # Parse the arguments and assign to global
    args = parser.parse_args()

    # Scan for single device using its MAC address
    status, devices = ble_scanner(args.mac, args.timeout, _ADVDATA, args.workingdir, args.debug)

    # Handle the ble scanner result
    # The json array should contain a single entry (index 0)
    if status:
        if len(devices) == 1:
            if _DEBUG:
                print(devices['address'], devices['name'], devices['advertisementdata'])
            devdata = decode_data(devices[0])
            # {'mac': 'A4:C1:38:D1:17:57', 'name': 'GVH5075_1757', 'status': 'OK', 'message': '', 'temperature': 16.5, 'humidity': 56, 'batterylevel': 95}
            print(devdata)
    else:
        print(f'[WARNING] Device {_MAC} not found.')

