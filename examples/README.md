## Examples using the BLE Scanner.

### Device Scanner
There are two examples which scan for a single or multiple devices.

The sensor data is not decoded.

### Sensor Decoder Scripts
The **Python sensor decoder** scripts are used to get & decode the sensor data and run the BLE Scanner as an external process.

The output, JSON object containing an array with one or more devices (sensors), is decoded according the data format specifications.

### Domoticz Home Automation System
For the **Domoticz Home Automation System**, there are examples on how to use the BLE Scanner (blescanner.py) in dzVents automation scripts.

There are two options on decoding and updating the Domoticz devices:
* Sensor data decoding from the JSON object returned by the BLE Scanner and Domoticz device update in the Domoticz dzVents script (preferred)).
* Sensor data decoding in Python Sensor Decoder Script from the JSON object returned by the BLE Scanner and update the Domoticz device in dzVents script.

**Notes**
* The automation script examples are written in in **dzVents** (based on Lua).
* The Python sensor decoder script runs asynchronous (not blocking the Domoticz system) to get the sensor data (as JSON object).
* The Python sensor decoder script calls the BLE Scanner (blescanner.py).
* The default scanning time is 10 seconds, but can be changed by setting the timeout argument in the dzVents script. Example 5 seconds: -t 5.
* The **Domoticz hardware controller "Dummy"** is used to create virtual devices, like a **Temp + Humidity device**, which are updated by the dzVents script.

#### Automation Script Decoding (dzVents)
The BLE Scanner runs asynchronous to get the sensor data as JSON object. The MAC address of the sensor is used as argument.
The sensor data is decoded and the Domoticz device is updated.

**Example Setup Govee 5075 Sensor**
* Copy Python script **blescanner.py** to the Domoticz folder **~domoticz/scripts/python**.
* Open a terminal on the Domoticz system and run **python blescanner.py** from the Domoticz folder **~domoticz/scripts/python** to get the Govee 5075 MAC address, like  {"address": "A4:C1:38:D1:17:57", "name": "GVH5075_1757"}.
* Add (or use an existing) Domoticz hardware controller **Dummy**.
* Create a virtual sensor type **Temp+Hum** from the Domoticz hardware controller **Dummy**.
* Note the **idx** of the new device.
* Add a new automation script from type **dzVents** > minimal. Clear the default content.
* Copy and paste the content of the file **domoticz_gvh5075.dzvents**.
* Set the **MAC address** and **idx** of the sensor in the table **sensors**, like s01 = {mac = "A4:C1:38:D1:17:57", idxth = 2, aftersec=0, active=true}.
* Set the automation script to **On** and **save**.
* Check the Domoticz log and the Temp+Hum device data.

#### Sensor Decoder Scripts (Python)
The Python sensor decoder script runs asynchronous to get the sensor data as JSON object. The MAC address of the sensor is used as argument.
The sensor data JSON object is parsed to update the Domoticz device, like a Temp + Humidity.

**Notes**
* The additional sensor script argument **workingdir** is required to run the BLE Scanner from the ~domoticz/scripts/python folder. Example (must end with /): -w scripts/python/.

**Example Setup Govee 5075 Sensor**
* Copy Python script **blescanner_gvh5075_decoder.py** to the Domoticz folder **~domoticz/scripts/python**.
* Copy Python script **blescanner.py** to the Domoticz folder **~domoticz/scripts/python**.
* Open a terminal on the Domoticz system and run **python blescanner.py** from the Domoticz folder **~domoticz/scripts/python** to get the Govee 5075 MAC address, like  {"address": "A4:C1:38:D1:17:57", "name": "GVH5075_1757"}.
* Add (or use an existing) Domoticz hardware controller **Dummy**.
* Create a virtual sensor type **Temp+Hum** from the Domoticz hardware controller **Dummy**.
* Note the **idx** of the new device.
* Add a new automation script from type **dzVents** > minimal. Clear the default content.
* Copy and paste the content of the file **domoticz_gvh5075_decoder.dzvents**.
* Set the **MAC address** and **idx** of the sensor in the table **sensors**, like s01 = {mac = "A4:C1:38:D1:17:57", idxth = 2, aftersec=0, active=true}.
* Set the automation script to **On** and **save**.
* Check the Domoticz log.

