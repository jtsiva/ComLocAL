#!/bin/bash
counter=0

while [ $counter -lt 50000 ]; do
	$(./send_to.sh "$1")
	let counter=counter+1
done
