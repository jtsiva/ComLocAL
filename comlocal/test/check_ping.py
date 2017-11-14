#!/usr/bin/python

from comlocal.core import Com
import time

def nope(msg):
	pass

def main():
	com = Com.Com()
	com.setReadHandler(nope)
	com.start()
	time.sleep(30)
	com.stop()





if __name__ == "__main__":
	main()