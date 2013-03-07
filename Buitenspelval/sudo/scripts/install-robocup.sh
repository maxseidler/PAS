#! /bin/bash
clear
setterm -background black -foreground red
message="
# This is a script that installs everything you need\n
# for the Robocup@Home BORG Team (Clones MAIN repository):\n
# OpenCV 2.2 with CUDA 3.2 & TBB & FireWire & SSE & Python 2.6 bindings\n
# Choregraphe suite 1.10.10 (SDK & Choregrape & Telepathe)\n
# Flann 1.6.8 & PyFlann & LibFreeNect & Cython 0.14.1
"
echo -e $message
if [ "$USER" == 'root' -o "$(whoami)" == 'root' ]; then
	echo "You should not run $0 as root ( $(whoami) )!"
	exit 1;
fi
echo "---------------------------------------------------------"
echo -e "\t--{ Begining installation for current user: $USER)"
echo -e "\t--{ Updating and installing dependencies : "
sudo apt-get -y update
sudo apt-get -y remove python-opencv mercurial
sudo apt-get -y autoremove
sudo apt-get -y install build-essential
sudo apt-get -y install cmake pkg-config libcppunit-dev
sudo apt-get -y install subversion git-core
sudo apt-get -y install wakeonlan openssh-server beep
sudo apt-get -y install libgtk2.0-dev
sudo apt-get -y install libavformat-dev libswscale-dev
sudo apt-get -y install libjasper1 libjasper-dev
sudo apt-get -y install libtbb-dev libv4l-dev
sudo apt-get -y install libglut3-dev libxmu-dev libxi-dev libusb-1.0-0-dev
sudo apt-get -y install libgstreamer0.10-0 libgstreamer0.10-0-dbg libgstreamer0.10-dev libgstreamer-plugins-base0.10-0 libgstreamer-plugins-base0.10-dev
sudo apt-get -y install libdc1394-22 libdc1394-22-dev libdc1394-utils
sudo apt-get -y install sun-java6-jdk sun-java6-jre
sudo apt-get -y install python-dev libpython2.6 python-dev libboost-python-dev
sudo apt-get -y install python-numpy python-scipy python-matplotlib python-sphinx

# libunicap2 libunicap2-dev libucil2 libucil2-dev libavfilter0 x264 libx264-dev
# http://downloads.sourceforge.net/project/opencvlibrary/opencv-unix/2.2/OpenCV-2.2.0.tar.bz2
# tar xjvf OpenCV-2.2.0.tar.bz2
# mv OpenCV-2.2.0 opencv

echo -e "\t--{ Finished updating and installing apt-get dependencies"
echo "---------------------------------------------------------"
echo -e "\t--{ Creating main folder: $HOME/Robocup"
mkdir -p ~/Robocup && cd ~/Robocup
withcuda="$(echo ${1} | tr 'A-Z' 'a-z')"
if [ "$withcuda" == "cuda" ]; then
	echo -e "\t--{ Downloading and installing Cuda 3.2 Toolkit"
	wget http://developer.download.nvidia.com/compute/cuda/3_2_prod/toolkit/cudatoolkit_3.2.16_linux_32_ubuntu10.04.run
	chmod +x cudatoolkit_3.2.16_linux_32_ubuntu10.04.run
	sudo ./cudatoolkit_3.2.16_linux_32_ubuntu10.04.run auto
	rm -rf cudatoolkit_3.2.16_linux_32_ubuntu10.04.run
	echo -e "\t--{ Downloading and installing Nvidia NPP 3.2"
	cd ~/Robocup
	mkdir -p CudaSDK && cd CudaSDK
	if [ ! -d $HOME/Robocup/CudaSDK/SDK ]; then
		wget http://developer.download.nvidia.com/compute/cuda/3_2_prod/toolkit/npp_3.2.16_linux_32.tar.gz
		tar -zxvf npp_3.2.16_linux_32.tar.gz
		rm -rf npp_3.2.16_linux_32.tar.gz
	fi
fi
echo -e "\t--{ Finished with dependencies for OpenCV"
echo "---------------------------------------------------------"
echo -e "\t--{ Updating your ~/.bashrc file ... "
echo "# ----> BORG CONFIG PATHS <---- " >> ~/.bashrc
echo "export PYTHONPATH=\$PYTHONPATH:/usr/local/lib/python2.6/site-packages" >> ~/.bashrc
sudo ldconfig
echo "---------------------------------------------------------"
echo -e "\t--{ Downloading and installing OpenCV 2.2"
if [ ! -d $HOME/Robocup/opencv ]; then
	cd ~/Robocup
	svn co https://code.ros.org/svn/opencv/trunk/opencv
else
	cd ~/Robocup/opencv
	svn update
fi
wait $!
cd ~/Robocup/opencv
mkdir -p release && cd release
rm -rf CMakeCache.txt
if [ "$withcuda" == "cuda" ]; then
	echo "export PATH=\$PATH:/usr/local/cuda/bin" >> ~/.bashrc
	echo "export LD_LIBRARY_PATH=\$LD_LIBRARY_PATH:/usr/local/cuda/lib" >> ~/.bashrc
	sudo ldconfig

	cmake -D CMAKE_BUILD_TYPE=RELEASE -D WITH_TBB=YES -D TBB_INCLUDE_DIRS=/usr/include/tbb -D OPENCV_BUILD_3RDPARTY_LIBS=ON -D USE_SSE=ON -D USE_SSE2=ON -D USE_SSE3=ON -D WITH_UNICAP=YES -D WITH_CUDA=YES -D CUDA_NPP_LIBRARY_ROOT_DIR=~/Robocup/CudaSDK/SDK -D CMAKE_INSTALL_PREFIX=/usr/local -D BUILD_PYTHON_SUPPORT=ON -D BUILD_EXAMPLES=ON -Wno-dev ..
else
	cmake -D CMAKE_BUILD_TYPE=RELEASE -D WITH_TBB=YES -D TBB_INCLUDE_DIRS=/usr/include/tbb -D OPENCV_BUILD_3RDPARTY_LIBS=ON -D USE_SSE=ON -D USE_SSE2=ON -D USE_SSE3=ON -D WITH_UNICAP=YES -D WITH_CUDA=NO -D CMAKE_INSTALL_PREFIX=/usr/local -D BUILD_PYTHON_SUPPORT=ON -D BUILD_EXAMPLES=ON -Wno-dev ..
fi
make 
sudo make install
sudo ldconfig
echo -e "\t--{ Finished installing OpenCV 2.2 (CUDA + TBB + Python)"
echo "---------------------------------------------------------"
echo -e "\t--{ Downloading and installing FLANN 1.6.8 "
cd ~/Robocup
if [ ! -d $HOME/Robocup/flann-1.6.8-src ]; then 
	wget http://www.cs.ubc.ca/~mariusm/uploads/FLANN/flann-1.6.8-src.zip
	unzip flann-1.6.8-src
	rm -rf ~/Robocup/flann-1.6.8-src.zip
fi
cd ~/Robocup/flann-1.6.8-src
make
sudo make install
echo -e "\t--{ Finished installing FLANN "
echo "---------------------------------------------------------"
echo -e "\t--{ Installing LibFreeNect for the Kinect "
cd ~/Robocup && mkdir -p kinect && cd kinect
if [ ! -d $HOME/Robocup/kinect/libfreenect ]; then 
	git clone https://github.com/OpenKinect/libfreenect.git
fi
cd ~/Robocup/kinect/libfreenect/ && mkdir release && cd release
cmake ..
make
sudo make install
sudo ldconfig
echo "---------------------------------------------------------"
echo -e "\t--{ Installing Cython 0.14.1 for LibFreeNect python bindings"
cd ~/Robocup
if [ ! -d $HOME/Robocup/Cython-0.14.1 ]; then
	wget http://cython.org/release/Cython-0.14.1.zip
	unzip Cython-0.14.1.zip
	rm -rf Cython-0.14.1.zip
fi
cd ~/Robocup/Cython-0.14.1
sudo python setup.py install
echo -e "\t--{ Finished installing Cython ... creating bindings"
cd ~/Robocup/kinect/libfreenect/wrappers/python
sudo python setup.py install
echo -e "\t--{ Finished installing LibFreeNect + Python Bindings"
#echo "---------------------------------------------------------"
#echo -e "\t--{ Installing OpenNI for the Kinect "
#mkdir ~/Robocup/kinect
#cd ~/Robocup/kinect
#git clone https://github.com/OpenNI/OpenNI.git
#cd OpenNI/Platform/Linux-x86/Build
#make && sudo make install
#cd ~/Robocup/kinect
#git clone https://github.com/boilerbots/Sensor.git
#cd Sensor
#git checkout ~/Robocup/kinect
#cd Platform/Linux-x86/Build
#make && sudo make install
#cd ~/Robocup/kinect
#wget http://www.openni.org/downloadfiles/openni-compliant-middleware-binaries/stable/54-primesense-nite-beta-build-for-for-ubuntu-10-10-x86-32-bit-v1-3-0/download
#tar -jxvf download
#rm -rf download
#cd Nite-1.3.0.17/Data
#sudo sed -i 's/^key=\"insert key here\"/key=\"0KOIk2JeIBYClPWVnMoRKn5cdY4=\"/' Sample-User.xml

echo -e "\t--{ Solving Kinect USB problems (creating video group and adding you there)"
sudo echo /etc/udev/rules.d/66-kinect.rules > '
#Rules for Kinect ####################################################
SYSFS{idVendor}=="045e", SYSFS{idProduct}=="02ae", MODE="0660",GROUP="video"
SYSFS{idVendor}=="045e", SYSFS{idProduct}=="02ad", MODE="0660",GROUP="video"
SYSFS{idVendor}=="045e", SYSFS{idProduct}=="02b0", MODE="0660",GROUP="video"
### END #############################################################
'
#sudo adduser $(whoami) video
o "---------------------------------------------------------"
echo -e "\t--{ Downloading Choregraphe Suite 1.10.10"
cd ~/Robocup/
if [ ! -d $HOME/Robocup/choregraphe-suite-1.10.10-linux ]; then
	wget --user=homerug --password='ImportSoul' http://www.ai.rug.nl/crl/uploads/Site/software/choregraphe-suite-1.10.10-linux.tar.gz
	tar -zxvf choregraphe-suite-1.10.10-linux.tar.gz
	rm -rf choregraphe-suite-1.10.10-linux.tar.gz
fi
sudo ldconfig
echo -e "\t--{ Finished adding Choregraphe ... "
echo "---------------------------------------------------------"
echo -e "\t--{ Installing Mercurial and cloning Main BORG repository"
sudo add-apt-repository ppa:mercurial-ppa/releases
sudo apt-get -y update
sudo apt-get -y install mercurial
cd ~/Robocup
if [ -d ~/.ssh/ ]
then
	hg clone ssh://hg@www.ai.rug.nl/repos/robotica
else
	echo -e "\t--{ You don't have a ~/.ssh/ folder, did you copy your keys?"
fi


#copy the speech recognition to the repository:

#Is not necessary
#wget http://www.ai.rug.nl/~shickend/speech.jar
#mv speech.jar $HOME/Robocup/robotica/Brain/src/speech/client/

echo -e "\t--{ Updating your ~/.bashrc file ... "
echo "# Aldebaran libs" >> ~/.bashrc
echo "export AL_DIR=\$HOME/Robocup/choregraphe-suite-1.10.10-linux" >> ~/.bashrc
echo "export PYTHONPATH=\$PYTHONPATH:\$AL_DIR/lib" >> ~/.bashrc
echo "export LD_LIBRARY_PATH=\$LD_LIBRARY_PATH:\$AL_DIR/lib" >> ~/.bashrc
echo "# Some more libs" >> ~/.bashrc
echo "export PYTHONPATH=\$PYTHONPATH:/usr/lib:/usr/local/lib" >> ~/.bashrc
echo "# BORG sys variable" >> ~/.bashrc
echo "export BORG=\$HOME/Robocup/robotica" >> ~/.bashrc
echo "# Add borg to path" >> ~/.bashrc
echo "export PYTHONPATH=\$PYTHONPATH:\$BORG/Brain/src" >> ~/.bashrc
echo -e "\t--{ Updating your /etc/hosts file"
if [ -f write_hosts.sh ]; then
sudo bash write_hosts.sh
fi
echo "export PATH=\$PATH:\$BORG/scripts" >> ~/.bashrc
echo -e "\t--{ Installation is finished ..."
echo -e "\t--{ Instructions on how to test are in the manual ... "
echo -e "\t--{ Python import test (you should not see any errors) "
PS1='$ ' # ubuntu default .bashrc thing
source ~/.bashrc # refresh shell
python -c "import cv" "import pyflann" "import naoqi" "import cython" "import freenect" "import numpy"
echo -e "\t--{ Updating system packages, you should restart afterwards"
sudo apt-get -y update > /dev/null
sudo apt-get -y autoremove > /dev/null
sudo apt-get -y upgrade > /dev/null
echo -e "\t--{ Would you like to restart now? (y/n): "
read -e RBT
if [ $RBT == 'y' -o $RBT == 'Y' ]; then
sudo reboot
fi
echo "---------------------------------------------------------"
