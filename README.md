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
:warning: Due to the Tilt's use of Bluetooth, you will need to be using either a Raspberry Pi 3 or a Bluetooth dongle to use this plugin.

## Installation
1. First, you must install the library that will allow the plugin to communicate with the Tilt over Bluetooth. Open a terminal window on your Raspberry Pi or use SSH and run the following command: 
```
sudo apt-get install python-bluez
```
2. Run the following command to allow the Bluetooth device to be acessible by any user: 
```
sudo setcap cap_net_raw+eip /usr/bin/python2.7
```
3. Click the **System** menu in CraftBeerPi, and then click **Add-On**.  Install the Tilt plugin by clicking the **Download** button, and when you receive a notification, reboot the Raspberry Pi.

## Configuration

### CraftBeerPi Configuration
1. In CraftBeerPi, click on the **System** menu, and then choose **Hardware Settings**.
2. Click the **Add** button in the Sensor section, and fill out the sensor properties:
    1. **Name**: Give the sensor a name. This is specific to this sensor reading, and does not need to match the Tilt color. It can be something like Wort Gravity or Tilt Temperature.
    2. **Type**: Choose TiltHydrometer.
    3. **Tilt Color**: This should be set to the color of your Tilt.
    4. **Data Type**: Each Tilt has two types of data that it reports, the Temperature and Gravity, so select the one that you are configuring for this particular sensor.    
    5. **Gravity Units**: *This field is only required if Data Type is set to Gravity*. The Tilt converts its readings into Specific Gravity by default. However you can choose one of three types here and it will be converted to that unit automatically. The choices are SG (Specific Gravity), Brix, and °P (Degrees Plato).
    7. Once you have filled out the sensor fields, click **Add**.
3. Repeat the above steps if you want additional sensors for the other data types that your Tilt reports, or if you have more than one Tilt, you can create sensors for those devices as well.
4. You can now add any of the Tilt sensors to kettles or fermenters in your brewery, or you can view their data on the dashboard or graph their data with the charts.
