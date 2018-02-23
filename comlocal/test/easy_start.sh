#!/bin/bash

twistd --logfile radmgr.log --pidfile radmgr.pid --python ../radio/RadioManager.tac
twistd --logfile wifi.log --pidfile wifi.pid --python ../radio/WiFiManager.tac
twistd --logfile dummy.log --pidfile dummy.pid --python ../radio/Dummy.tac
twistd --logfile com.log --pidfile com.pid --python ../core/Com.tac
