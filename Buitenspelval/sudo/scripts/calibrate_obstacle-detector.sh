#!/bin/bash

echo -e "\n>> Calibrating on Kinect-nav"
ssh -X borg@kinect-nav -T "cd ~/Robocup/robotica/Brain/src/vision/obstacledetectorutil; killall python; killall python -9; python calibrator.py"
echo -e "\m>> Done calibration"
