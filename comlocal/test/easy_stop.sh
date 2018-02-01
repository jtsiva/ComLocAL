#!/bin/bash

kill $(cat com.pid)
kill $(cat radmgr.pid)
kill $(cat wifi.pid)