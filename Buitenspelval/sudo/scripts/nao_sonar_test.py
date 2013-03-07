#!/usr/bin/python
# Modified example from:
# http://www.aldebaran-robotics.com/documentation/naoqi/sensors/alsonar.html
# Before running this command please check your PYTHONPATH is set correctly to the folder of your pynaoqi sdk.

from naoqi import ALProxy 

import time

# Set the IP address of your NAO.
ip = "10.0.0.147"

# Connect to ALSonar module.
sonarProxy = ALProxy("ALSonar", ip, 9559)

# Subscribe to sonars, this will launch sonars (at hardware level) and start data acquisition.
sonarProxy.subscribe("myApplication")

#Now you can retrieve sonar data from ALMemory.
memoryProxy = ALProxy("ALMemory", ip, 9559)

while True:
    # Get sonar left first echo (distance in meters to the first obstacle).
    left = memoryProxy.getData("Device/SubDeviceList/US/Left/Sensor/Value")

    # Same thing for right.
    right = memoryProxy.getData("Device/SubDeviceList/US/Right/Sensor/Value")

    print "%.2f, %.2f" % (left, right)

    time.sleep(0.5)
