#!/bin/sh
#Archives the PAS branch while removing the .git directory.

git archive PAS --prefix=sudo/ | bzip2 > "borg_src_"`date +"%F"`".tar.bz2"
