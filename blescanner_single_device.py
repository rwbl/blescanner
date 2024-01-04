#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File: blescanner_single_device.py
# Date: 20240104
# Author: Robert W.B. Linn
# Example: Scan for a single BLE device and parse the data published.
# Dependencies: blescanner.py - Tool to scan for Bluetooth Low Energy (BLE) devices.

import subprocess
import json

# Debug flag 0 (OFF), 1(ON)
_DEBUG = 0

# Timeout of the subprocess running the blescanner.py.
# The value must be > parameter mode 1 timeout used by the blescanner.py.
_TIME_OUT_SUBPROCESS = 30

# Timeout running the ble scanner.
_TIME_OUT = 5

# Advertised data
_ADVDATA = 1

# Single device MAC address
_MAC = "A4:C1:38:D1:17:57"

# BLE handler External Python script
# The Domoticz parameter homefolder is used to set the path = see onstart
_BLE_HANDLER = "blescanner.py"
_PYTHON_COMMAND = "python"
_BLESCANNER = "blescanner.py"

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
    # Handle the result
    if status:
        # print(f'devices ={devices}')
        for device in devices:
            print(device['address'], device['name'], device['advertisementdata'])
    else:
        print('[WARNING] Device not found.')

