# house
Code for controlling house light and measuring temperature and humidity using a Raspberry Pi and [ANAVI-light HAT](https://www.crowdsupply.com/anavi-technology/light-phat)


## Installation

### Software

Enabling of i2c ports through `raspi-config` is needed. A python3 installation is also needed to run the program and not detailed in this document. 

These required libraries were installed as:

```
sudo apt-get install python-rpi.gpio
sudo apt-get install wiringpi
sudo -H pip install psutil
sudo -H pip3 install luma.oled
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

## Contribute

This is a preliminary release. File issues to contribute to this project. 