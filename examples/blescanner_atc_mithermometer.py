#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
File: blescanner_blescanner_atc_mithermometer.py
Date: 20240105
Author: Robert W.B. Linn
Scan for a single BLE device XIAOMI Mijia Bluetooth Thermometer 2 Wireless Smart Electric Digital Hygrometer Thermometer and decode the data published.
Dependencies: blescanner.py - Tool to scan for Bluetooth Low Energy (BLE) devices.

Firmware:
Custom firmware is used enabling listen to advertisements in passive mode. No connection required.
Reference & Credits: https://github.com/atc1441/ATC_MiThermometer

Dataformat:
The custom firmware advertises 15 bytes.
Example: C2745238C1A4 7C 06 F1 18 C7 09 2B 17 0E

Bytes 0-6 (6): MAC = C2745238C1A4
Bytes 7-8 (2): Temp = 7C06 > 067C = DEC 16.6
Bytes 9-10 (2): Hum = F118 > 18F1 = DEC 63.85
Bytes 11-12 (2):Voltage = C709 > 09C7 = DEC 2503
Byte 13 (1): Battery = 2B > 2B = DEC 43
Byte 14 (1): Counter Not used
Byte 15 (1): Flags Not used

Example
Advertised data received: C2745238C1A45907DB15130A36830E, len=15
Data used to publish as json object: 5907DB15130A36, len=7
Result json object:
{"status": "OK", "message": "", "mac": "A4:C1:38:52:74:C2", "name": "ATC_38A90C", "temperature": 18.81, "humidity": 56, "voltage": 2.58, "batterylevel": 54}
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
_MAC = "A4:C1:38:38:A9:0C"

# BLE handler External Python script
# The Domoticz parameter homefolder is used to set the path = see onstart
_BLE_HANDLER = "blescanner.py"
_PYTHON_COMMAND = "python"
_BLESCANNER = "blescanner.py"

# Device Specifics
# Data contains 15 bytes
_ADVERTISED_DATA_LENGTH = 15
_ADDRESS_KEY = "address"
_NAME_KEY = "name"
_ADVERTISEMENT_KEY = "advertisementdata"
# UUID Service Data
_UUID_SERVICE_DATA = '0000181A-0000-1000-8000-00805F9B34FB'

################################################################################
# DECODE DATA
################################################################################

def decode_data(data):
    """Decode the data into a json object with properties."""
    
    # _DEBUG = 1

    if _DEBUG:
        # {'address': 'A4:C1:38:38:A9:0C', 'name': 'ATC_38A90C', 'local_name': 'ATC_38A90C', 'advertisementdata': {'service_data': True, '0000181A-0000-1000-8000-00805F9B34FB': '0CA93838C1A45A054D1B150B5B0C0E', 'rssi': -56}}
        print(f"[DEBUG decode_data]{data}")

    # Get the macaddress and the device name.
    macaddress = data[_ADDRESS_KEY]
    name = data[_NAME_KEY]

    # Get the data from service uuid and convert from string to hex
    data = bytes.fromhex(data[_ADVERTISEMENT_KEY][_UUID_SERVICE_DATA])

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
        # Get the THVB data bytes 6 to 13 from the advertised bytearray
        data = data[6:13]

        if _DEBUG:
            print(f"[DEBUG decode_data] {data.hex().upper()}, len={len(data)}")

        # Unpack the bytearray data holding 7 bytes to a tuple with 4 items T, H, V, B
        # <=little indian, H=unsigned short (2 bytes * 3), B=unsigned char (1 byte) = total 7 bytes
        dat = struct.unpack('<HHHB', data)
        
        if _DEBUG:
            print("[DEBUG] data tuple:", dat, len(dat), "items")
            # (1788, 69, 2541) 4 items

        # Create the dict which is printed (=returned)
        result = {
            "status": "OK",
            "message": "",
            "mac": macaddress,
            "name": name,
            "temperature": round(dat[0] / 100,2),	#°C
            "humidity": round(dat[1] / 100),		#%RH
            "voltage": round(dat[2] / 1000,2),		#V
            "batterylevel": dat[3]					#%
        }
        
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
            # {'status': 'OK', 'message': '', 'mac': 'A4:C1:38:38:A9:0C', 'name': 'ATC_38A90C', 'temperature': 15.51, 'humidity': 66, 'voltage': 2.84, 'batterylevel': 91}
            print(devdata)
    else:
        print(f'[WARNING] Device {_MAC} not found.')

