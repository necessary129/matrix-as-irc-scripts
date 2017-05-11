#!/bin/bash

user=$1
shift
for arg; do
./give-ops.py -i $user -a "#pirateirc_$arg:diasp.in"
done
