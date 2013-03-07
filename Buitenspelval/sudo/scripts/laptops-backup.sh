#!/bin/bash
clear
message='\n
# This script backups these folders: /usr /opt /etc /var /lib \n
# /home/HOSTNAME/user on this machine to a specified usb device.\n
# If there is already a bacup on the device\n
# it will just add the changes from the initial backup\n'
echo -e $message
echo -e "> These are the mounted devices on your machine:\n"
#sudo mount | grep on\ /m
df -H | grep /dev/sd
echo -e "\n> Where would you like to store backups?:\n> "
read backup_location
if [ ! -e $backup_location ]; then
	echo -e "\n> There is no such device..."
	exit 1;
fi
echo -e "\n> Are you sure you want to backup to this location?(y/n) :\n> " 
sudo df -H | grep $backup_location
read confirmation && confirmation="$(echo $confirmation | tr 'A-Z' 'a-z')"
if [ $confirmation != "y" -a $confirmation != "yes" ]; then
	echo "\n> Stopped ... "
	exit 1;
fi
echo -e "Backup only home folder?(y/n) :\n> "
read only_home
if [ $only_home == "y" -a $only_home == "yes" ]; then
	echo -e "\n> Starting backup ... " 
	sudo rsync -avz /home $backup_location/$HOSTNAME
	exit 1;
fi
echo -e "\n> Starting backup ... " 
sudo rsync -avz --progress /usr $backup_location
sudo rsync -avz --progress /opt $backup_location
sudo rsync -avz --progress /etc $backup_location
sudo rsync -avz --progress /var $backup_location
sudo rsync -avz --progress /lib $backup_location

