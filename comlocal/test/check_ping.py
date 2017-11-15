#!/usr/bin/python

from comlocal.core import Com
import time

def nope(msg):
	pass

def main():
	com = Com.Com()
	com.setReadHandler(nope)
	try:
		com.start()
		time.sleep(30)
	finally:
		com.stop()





if __name__ == "__main__":
	main()