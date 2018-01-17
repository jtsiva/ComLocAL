#!/usr/bin/python

from comlocal.core import Com
import threading
import time
import random


com = Com.Com()

def run():
	if run.repeat > 0:
		print com.write({'type':'cmd','cmd':'getNeighbors'})
		run.repeat -= 1
		threading.Time(5,run).start()

def main():
	run.repeat = 5
	com.start()
	try:
		run()
		time.sleep(30)
	finally:
		com.stop()
#

if __name__ == "__main__":
	main()