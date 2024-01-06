## Examples using the BLEScanner.

The Python scripts are running the BLEScanner as an external process.

The output, JSON object containing an array with one or more devices (sensors), is decoded according the data format specifications.

### Domoticz Home Automation System
For the **Domoticz Home Automation System** some examples on how to use the Python scripts in automation scripts.

The automation script examples are written in in dzVents (based on Lua).

The Python script runs asynchronous (not blocking the Domoticz system) to get the sensor data (as JSON object).

Note the addition script argument **workingdir** which is required to run the blescanner from the ~domiticz/scripts/python folder.
