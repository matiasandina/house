# house
Code for controlling house light and measuring temperature and humidity using a Raspberry Pi and [ANAVI-light HAT](https://www.crowdsupply.com/anavi-technology/light-phat)


## Installation

### Software

Enabling of i2c ports through `raspi-config` is needed. A python3 installation is also needed to run the program and not detailed in this document. 


> [!CAUTION]
> Python < 3.8 will need different environment than what's tested in 3.8+. We have found issues with library incompatibilities. **It's recommended that you use a virtual environment!**

Please see `install.sh`. This will create a virtual environment and set the software in a proper way. You can also manually `pip install` using:

```
pip install adafruit-circuitpython-bh1750==1.1.0 adafruit-circuitpython-busdevice==5.1.8 adafruit-circuitpython-HTU21D==0.11.4 adafruit-circuitpython-register==1.9.8 adafruit-circuitpython-typing==1.7.0 RPi.GPIO==0.7.0

```

If you want to use the latest libraries (not recommended), the required libraries can be installed as:

```
sudo apt-get install python-rpi.gpio
sudo apt-get install wiringpi
sudo -H pip3 install psutil
sudo -H pip3 install luma.oled
sudo pip3 install numpy
sudo pip3 install adafruit-circuitpython-htu21d
sudo pip3 install adafruit-circuitpython-bh1750
```



### Hardware

The position of the pins in the code is as follows. The RGB lights being used have a fourth channel with true white that was connected to the blue pin. If using RGB only lights, all pins should be set to high to create the desired light color and intensity.

```
red_pin = 9
green_pin = 10 
# it's nice to have the blue pin connected to the white pin maybe
# this real white is better than the bluish combination of the RGB
blue_pin = 11
```

We are using a generic [0.96'' IIC OLED SSD1306](https://www.amazon.com/SSD1306/s?k=SSD1306) to provide feedback regarding the Raspberry Pi IP, Temperature and Humidity.

## Usage

You can use this by running the following command in command line.

```
pi@raspberrypi:~/house $ python3 house.py
```

Alternatively, you can install this to run in the background using `pyinstaller`

```
pi@raspberrypi:~/house $ pyinstaller house.py -w -F

```

You can check that this is running by calling

```
pi@raspberrypi:~/house $ ./dist/house 
```
You can also check that the process is running in the Task manager.

In day to day use, you can just double-click the ./dist/house application and it will launch in the background. You can also have a desktop icon. Just copy the provided `house.desktop` and paste it into your desktop. Just a double-click and you are good to go!

Remember to check if the process is running in the Task Manager. You can also use the task manager to kill the program.

![](img/icon_task_manager.png?raw=true)

Data will be saved into the `dist/` folder when using `house` this way.

> Beware you might need to edit the path! The provided desktop is hardcoded to `/home/pi/house/dist/house`. If your user or path differs, you will need to tweak this.


## Data Base Sync

Very preliminary syncing to a database (this project uses a Synology NAS but should work with other Linux enabled systems).
This process was kept manual for security reasons, but it could be automated if the user wants to use `sshpass` during setup. Since it's once per device, it might be good to do it manually.

```
# on each RPi
ssh-keygen -t rsa -b 2048 -N "" -f ~/.ssh/id_rsa # key might already exist, you don't need to overwrite it
ssh-copy-id -i ~/.ssh/id_rsa.pub -p port user@database_ip 
# test that you can access
ssh -p 'port' 'user@database_ip'
exit # <- exit out of the database

```

Copy and manually modify your keys

```
cp db_keys.yaml secret_db_keys.yaml
nano secret_db_keys.yaml
# edit your file here
```

## Dashboard App

A very preliminar dashboard app was made to get data from the server and display it on a table.
You are also advised to run this from a virtual environment with dash (see `dash_requirements.txt`).

## Contribute

This is a preliminary release. File issues to contribute to this project. 
