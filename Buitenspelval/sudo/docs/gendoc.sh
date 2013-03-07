#!/bin/bash
#Simple script that recursively iterates over all *.tex files and compiles it with pdflatex.

ROOT_DIR=$(pwd)
for f in $(find ./ -name '*.tex');
do
    cd $(dirname $f)
    pdflatex $(basename $f)
    cd $ROOT_DIR
done

