# Tilt Hydrometer Plugin for CraftBeerPi 3.0

Allows your Tilt digital hydrometer to send data to CraftBeerPi 3.0, such as the current temperature and gravity readings. The plugin allows you to create multiple sensors, each of which is associated with a different data type that the Tilt is capturing, so that you can use these sensors as you would any other sensor in CraftBeerPi.  You can also use multiple Tilt devices for different fermentation chambers at the same time. See below for setup instructions and some screenshots of the configuration options.

This plugin is based on the work of several others who developed the necessary Bluetooth and Tilt communications libraries:

- PyTilt: https://github.com/atlefren/pytilt
- iBeacon-Scanner: https://github.com/switchdoclabs/iBeacon-Scanner-
- PyBluez: https://github.com/karulis/pybluez

## Screenshots

![tilt1](https://user-images.githubusercontent.com/29404417/28493425-ef13c104-6ee4-11e7-9eab-b5dcdea6e40a.PNG)

![tilt2](https://user-images.githubusercontent.com/29404417/28493426-04ad66b4-6ee5-11e7-88f1-84acceb543a4.PNG)

## Requirements
:warning: Due to the Tilt's use of Bluetooth, you will need to be using either a Raspberry Pi with built-in Bluetooth (such as Raspbery Pi 3 or Raspberry Pi Zero W) or a Bluetooth dongle to use this plugin.

## Installation
1. First, you must install the library that will allow the plugin to communicate with the Tilt over Bluetooth. Open a terminal window on your Raspberry Pi or use SSH and run the following command: 
```
sudo apt-get install python-bluez
```
2. Install the NumPy library required by the Tilt plugin:
```
sudo pip install numpy
```
3. Run the following command to allow the Bluetooth device to be acessible by any user: 
```
sudo setcap cap_net_raw+eip /usr/bin/python2.7
```
4. Click the **System** menu in CraftBeerPi, and then click **Add-On**.  Install the Tilt plugin by clicking the **Download** button, and when you receive a notification, reboot the Raspberry Pi.

## Configuration

### CraftBeerPi Configuration
1. In CraftBeerPi, click on the **System** menu, and then choose **Hardware Settings**.
2. Click the **Add** button in the Sensor section, and fill out the sensor properties:
    1. **Name**: Give the sensor a name. This is specific to this sensor reading, and does not need to match the Tilt color. It can be something like Wort Gravity or Tilt Temperature.
    2. **Type**: Choose TiltHydrometer.
    3. **Tilt Color**: This should be set to the color of your Tilt.
    4. **Data Type**: Each Tilt has two types of data that it reports, the Temperature and Gravity, so select the one that you are configuring for this particular sensor.    
    5. **Gravity Units**: *This field is only required if Data Type is set to Gravity*. The Tilt converts its readings into Specific Gravity by default. However you can choose one of three types here and it will be converted to that unit automatically. The choices are SG (Specific Gravity), Brix (or °Bx), and Plato (or °P).
    6. **Calibration Point 1-3***: *Optional*. These fields allow you to calibrate your Tilt by entering an uncalibrated reading from the Tilt and then the desired, calibrated value. The format to use is ***uncalibrated value* = *actual value*** (spacing is optional). More info on calibration is in the section below.
    7. Once you have filled out the sensor fields, click **Add**.
3. Repeat the above steps if you want additional sensors for the other data types that your Tilt reports, or if you have more than one Tilt, you can create sensors for those devices as well.
4. You can now add any of the Tilt sensors to kettles or fermenters in your brewery, or you can view their data on the dashboard or graph their data with the charts.

### Tilt Calibration
You can use the Calibration Point fields to calibrate your Tilt, much like when using the standalone Tilt app. Here are some examples of ways you can calibrate your Tilt with this plugin.

- You can perform the *Tare in Water* procedure by placing the Tilt in water, taking a reading, and entering the value in a Calibration Point field in the format **1.002 = 1** (change the first number to your specific reading). 
- To fine tune the calibration even more, you can make a low and/or high gravity calibration point by taking readings of one or two solutions with a known gravity and enter those readings as ***tilt reading* = *solution's actual gravity***.
- If you enter only a single calibration point, the difference will be applied to every reading equally. So you could enter **0 = 5** if you just want 5 added to every reading that the Tilt takes, or **5 = 0** if you want to subtract 5 from every reading.  If you enter two or more calibration points, a linear relationship between the points will be determined and used to adjust the readings accordingly (known as linear regression).
- These calibration procedures work the same for both gravity readings and temperature readings, and are calculated after the conversion to the desired units (°C to °F, SG to Brix), so you should calibrate your Tilt with the units set to what they will be when you use it for actual brewing.

