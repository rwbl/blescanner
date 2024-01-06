## Examples using the BLEScanner.

The Python scripts are running the BLEScanner as an external process.

The output, JSON object containing an array with one or more devices (sensors), is decoded according the data format specifications.

### Domoticz Home Automation System
For the **Domoticz Home Automation System**, there are examples on how to use the Python scripts in automation scripts.

* The automation script examples are written in in **dzVents** (based on Lua).
* The Python script runs asynchronous (not blocking the Domoticz system) to get the sensor data (as JSON object).
* The additional script argument **workingdir** is required to run the blescanner from the ~domoticz/scripts/python folder. Example (must end with /): -w scripts/python/
* The default scanning time is 10 seconds, but can be changed by setting the timeout argument. Example 5 seconds: -t 5
