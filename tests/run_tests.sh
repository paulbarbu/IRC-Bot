#!/bin/sh

python2.7 -m unittest cmds_tests

#coverage run --source=../src --omit='../src/lib/*' cmds_tests.py
#coverage report -m
