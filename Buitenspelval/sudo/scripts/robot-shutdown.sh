#! /bin/bash
MSG="Remote shutdown initiated"
echo -e "\n> Password:"
stty -echo
read PWD
stty echo
echo -e "\n> ${MSG}"

# brain
if [ $HOSTNAME != 'brain' ]; then
ssh brain -T "echo ${PWD} | sudo -S shutdown -h now '${MSG}' && exit" > /dev/null
fi
# vision-front
ssh vision-front -T "echo ${PWD} | sudo -S shutdown -h now '${MSG}' && exit" > /dev/null
# vision-back
ssh vision-back -T "echo ${PWD} | sudo -S shutdown -h now '${MSG}' && exit" > /dev/null
# kinect-main
ssh kinect-main -T "echo ${PWD} | sudo -S shutdown -h now '${MSG}' && exit" > /dev/null
# kinect-nav
ssh kinect-nav -T "echo ${PWD} | sudo -S shutdown -h now '${MSG}' && exit" > /dev/null
#pioneer
ssh pioneer -T "echo ${PWD} | sudo -S shutdown -h now '${MSG}' && exit" > /dev/null

echo -e "\n> Waiting 5 seconds then checking if shutdown was successful"
sleep 5

bash robot-status.sh
