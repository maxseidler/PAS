#!/bin/bash

# Check if it's already in there ...
grep "brain" /etc/hosts -q && found=true

if [ ! $found ]; then

echo "---------------------------------------------------------"
echo "Updating your hosts file with the laptop names..."
echo "# BORG Laptop Names" >> /etc/hosts
echo "192.168.0.1	brain" >> /etc/hosts
echo "192.168.0.2	vision-front" >> /etc/hosts
echo "192.168.0.3	vision-back" >> /etc/hosts
echo "192.168.0.4	kinect-main" >> /etc/hosts
echo "192.168.0.5	kinect-nav" >> /etc/hosts
echo "192.168.0.10	nao" >> /etc/hosts
echo "192.168.0.20	pioneer" >> /etc/hosts
echo "---------------------------------------------------------"

else

echo ">> The /etc/hosts file appears to be correct. Check all entries manually if you have problems ... "

fi
