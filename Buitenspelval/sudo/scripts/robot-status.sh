#!/bin/bash

echo -e "\n>> Checking status of laptops, Nao and Pioneer ...\n"

while read ip host
do
    if [[ $ip == 192.* ]]; then
        ping -c 1 -W 1 ${ip} > /dev/null 2> /dev/null
        if [ $? -eq 0 ]; then
            echo -e "> ${host} \t is UP"
        else
            echo -e "> ${host} \t is DOWN"
        fi
    fi
done < /etc/hosts
