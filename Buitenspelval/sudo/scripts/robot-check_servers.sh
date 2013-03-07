#!/bin/bash

CUR_HOST=`hostname`
if [[ "$CUR_HOST" != "brain" && "$LAPTOPS" == "" ]]
then
    echo "====================================================================="
    echo "Not running on Brain laptop and LAPTOPS environmental variable is not"
    echo "set, so not starting communicators or pioneercontroller"
    echo "====================================================================="
    exit 0
fi

# Defaults
PIONEER_PORT=12345
COMMUNICATOR_PORT=49152

for i in $*
do
    case $i in
        --pioneer-port=*)
        PIONEER_PORT=`echo $i | sed 's/[-a-zA-Z0-9]*=//'`
        ;;
        --communicator-port=*)
        COMMUNICATOR_PORT=`echo $i | sed 's/[-a-zA-Z0-9]*=//'`
        ;;
        *)
            LAPTOPS="$LAPTOPS $i"
        ;;
    esac
done

if [ "$LAPTOPS" == "" ]
then
    LAPTOPS="vision-front kinect-main kinect-nav pioneer"
fi
if [ "$LAPTOPS" == "none" ]
then
    LAPTOPS=""
fi

WAIT="0"

check_communicator () {
    HOST=$1
    python $BORG/Brain/src/communicator/tester.py $HOST $COMMUNICATOR_PORT > /dev/null
    STARTED=$?
    if [ "$STARTED" != "0" ]
    then
        WAIT="1"
        echo -n "Starting communicator on $HOST... "
        if [ "$HOST" == "localhost" ]
        then
            echo "local... "
            killall python -9; sleep 5 ; cd $BORG/Brain/src/communicator ; DISPLAY=:0 python communicator.py $COMMUNICATOR_PORT &
        else
            echo "SSH... "
            ssh -f -C -X borg@$HOST "killall python -9; sleep 5 ; cd \$BORG/Brain/src/communicator ; DISPLAY=:0 python communicator.py $COMMUNICATOR_PORT"
        fi
        STARTED=$?
        if [ "$STARTED" != "0" ]
        then
            echo "WARNING: Communicator failed to start on $HOST on port $COMMUNICATOR_PORT"
            return 1
        else
            echo "Ok."
        fi
    else
        echo "Communicator on $HOST is already running on port $COMMUNICATOR_PORT"
    fi
    return 0
}

check_pioneer () {
    HOST=$1
    python $BORG/Brain/src/pioneercontrol/pioneer_tester.py $HOST $PIONEER_PORT > /dev/null
    STARTED=$?
    if [ "$STARTED" != "0" ]
    then
        WAIT="1"
        echo -n "Starting pioneercontroller on $HOST... "
        ssh -f -C -X borg@$HOST "killall motionController -9 ; sleep 5 ; \$HOME/pioneercontroller/motionController $PIONEER_PORT"
        STARTED=$?
        if [ "$STARTED" != "0" ]
        then
            echo "WARNING: Pioneercontroller failed to start on $HOST on port $PIONEER_PORT"
            return 1
        else
            echo "Ok."
        fi
    else
        echo "Pioneercontroller on $HOST is already running on port $PIONEER_PORT"
    fi
    return 0
}

RESULT=0
for host in $LAPTOPS
do
    if [ "$host" == "pioneer" ]
    then
        check_pioneer $host
        RES=$?
    else
        check_communicator $host
        RES=$?
    fi
    if [ "$RES" != "0" ]
    then
        RESULT=1
    fi
done

if [ "$WAIT" == "1" ]
then
    echo "Some servers were started or restarted. Giving them time to initalize. Hold on..."
    sleep 6
fi

if [ "$RESULT" == "0" ]
then
    echo "Communicator should now be running on port $COMMUNICATOR_PORT on all laptops"
    exit 0
else
    echo "WARNING: The communicator was not started on all laptops"
    exit 1
fi

