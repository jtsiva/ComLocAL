#!/bin/bash

payload="a"
count=10000

for delay in ".1" ".01" ".001" ".0001"
do
	for i in `seq 1 3`;
	do
		echo "delay: "$delay
		ssh pi@192.168.0.2 ComLocAL/comlocal/test/one-way.py -p 6.0 >> data/receiver.txt &
		ssh pi@192.168.0.49 ComLocAL/comlocal/test/one-way.py -c $count -s -d 0 -m $payload -p $delay >> data/sender.txt
		sleep 10
	done
done