# Raspicam
A multispectral camera application for the compute module of Raspberry Pi

The scripts use the dual cameras of the compute module.


# Requirements:
# Pip 3,
# Python 3,
# Picamera module,
# Opencv, 
# Opencv-contrib,


# Run the scripts from the home directory as follows:
# python3 Raspicam/foldertest.py & python3 Raspicam/picamera.py

Foldertest.py will create a new directory in your Pictures folder with a timestamp name (e.g. 2018-08-23_07:34:12).
Picamera.py will then join the recently created folder, and capture images with both cameras using the presets.
