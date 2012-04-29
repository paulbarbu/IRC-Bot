#!/bin/sh

if [ "-c" = $1 ]
then
    coverage run --source=../src --omit='../src/lib/*' --branch tests.py && coverage report -m
else
    python2.7 -m unittest discover -p '*_tests.py'
fi
