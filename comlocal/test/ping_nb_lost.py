#!/usr/bin/python

from comlocal.core import Com
import threading
import time
import random

def start():
	com = Com.Com()
	
	try:
		com.start()
		time.sleep(20)
	finally:
		com.stop()

def main():
	threading.Timer(random.randint(0,15), start).start()
#

if __name__ == "__main__":
	main()