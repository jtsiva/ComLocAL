#!/bin/bash

delay=.001
count=10000

for size in 1024 2048
do
	payload=$(./genString.py -n $size)
	for i in `seq 1 3`;
	do
		echo "size: "$size
		ssh pi@192.168.0.2 ComLocAL/comlocal/test/one-way.py -p 6.0 >> data/receiver.txt &
		ssh pi@192.168.0.49 ComLocAL/comlocal/test/one-way.py -c $count -s -d 0 -m $payload -p $delay >> data/sender.txt
		sleep 30
	done
done