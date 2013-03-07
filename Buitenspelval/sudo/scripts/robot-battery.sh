#!/bin/bash

echo "------------------------------------------------"
echo -e "\vHostname $HOSTNAME\n"

acpi -V | grep -P ", [0-9]{1,3}%"

acpi -V | grep -P ", [0-9]{1,3}.[0-9] degrees"

echo "------------------------------------------------"
