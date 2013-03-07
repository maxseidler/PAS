#! /bin/bash

which="$(echo ${1} | tr 'A-Z' 'a-z')"

if [ -z $which ]; then

	echo ">> Sending magic packets to start-up ALL laptops"
	# brain
	wakeonlan 00:18:8b:d1:57:c2
	# vision-front
	wakeonlan 00:1c:23:05:d1:71
    # vision-back
    # wakeonlan 00:1c:23:09:48:9a
	# kinect-main
	wakeonlan 00:1c:23:09:47:db
	# kinect-nav
	wakeonlan 00:24:e8:c6:8a:88

else
	echo ">> Sending magic packets to $which"
	case "$which" in

		"brain") wakeonlan 00:18:8b:d1:57:c2 ;;

		"vision-front") wakeonlan 00:1c:23:05:d1:71 ;;

        # "vision-back") wakeonlan 00:1c:23:09:48:9a ;;

		"kinect-main") wakeonlan 00:1c:23:09:47:db ;;

		"kinect-nav") wakeonlan 00:24:e8:c6:8a:88 ;;

		*) echo ">> Unknown host: $which" ;;
	esac
fi

echo ">> Waiting 30 seconds, then checking for status, press Ctrl+C to cancel..."
# wait 30 seconds
sleep 30

# check which hosts are online
bash robot-status.sh
