## Examples using the BLEScanner.

The Python scripts are running the BLEScanner as an external process.

The output, JSON object containing an array with one or more devices (sensors), is decoded according the data format specifications.

### Domoticz Home Automation System
For the **Domoticz Home Automation System**, there are examples on how to use the Python scripts in automation scripts.

* The automation script examples are written in in **dzVents** (based on Lua).
* The Python script runs asynchronous (not blocking the Domoticz system) to get the sensor data (as JSON object).
* The additional script argument **workingdir** is required to run the blescanner from the ~domoticz/scripts/python folder. Example (must end with /): -w scripts/python/.
* The default scanning time is 10 seconds, but can be changed by setting the timeout argument in the dzVents script. Example 5 seconds: -t 5.
* The **Domoticz hardware controller "Dummy"** is used to create virtual devices, like a **Temp + Humidity device**, which are updated by the dzVents script.

**Example Setup Govee 5075 Sensor**
* Copy Python script **blescanner_gvh5075.py** to the Domoticz folder **~domoticz/scripts/python**.
* Copy Python script **blescanner.py** to the Domoticz folder **~domoticz/scripts/python**.
* Open a terminal on the Domoticz system and run **python blescanner.py** from the Domoticz folder **~domoticz/scripts/python** to get the Govee 5075 MAC address, like  {"address": "A4:C1:38:D1:17:57", "name": "GVH5075_1757"}.
* Add (or use an existing) Domoticz hardware controller **Dummy**.
* Create a virtual sensor from type **Temp+Hum** from the Domoticz hardware controller **Dummy**.
* Note the **idx** of the new device.
* Add a new automation script from type **dzVents** > minimal. Clear the default content.
* Copy and paste the content of the file **domoticz_gvh5075.dzvents**.
* Set the **MAC address** and **idx** of the sensor in the table **sensors**, like s01 = {mac = "A4:C1:38:D1:17:57", idxth = 2, aftersec=0, active=true}.
* Set the automation script to **On** and **save**.
* Check the Domoticz log.
