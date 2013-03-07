#!/bin/bash
#Simple script that recursively iterates over all *.pdf files and compiles it into a single zip into /tmp/borg_docs_<date>.tar.gz

TMP_DIR="borg_docs/"

#Make sure we do not mess up some existing stuff:
if [ -d "$TMP_DIR" ];
then
    echo "ERROR: Temporarly directory $TMP_DIR already exists, aborting..."
    echo "Remove $TMP_DIR first to make this script work (and verify that you really want to remove it!)."
    exit 1
fi

mkdir -p $TMP_DIR

#Collect all *.pdf's:
ROOT_DIR=$(pwd)
for f in $(find ./ -name '*.pdf');
do
    mkdir -p $TMP_DIR$(dirname $f)
    cp $f $TMP_DIR$(dirname $f)
done

tar -zcvf "borg_docs_"`date +"%F"`".tar.gz" $TMP_DIR

#rm -rf $TMP_DIR
