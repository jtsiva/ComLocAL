#!/bin/bash

twistd --logfile com.log --pidfile com.pid --python ../core/Com.py
twistd --logfile radmgr.log --pidfile radmgr.pid --python ../radio/RadioManager.py
twistd --logfile wifi.log --pidfile wifi.pid --python ../radio/WiFiManager.py