#!/bin/bash

def_host=localhost
def_port=10267

HOST=${2:-$def_host}
PORT=${3:-$def_port}

echo -n "$1" | nc -p 10666 -4uw 0 $HOST $PORT
