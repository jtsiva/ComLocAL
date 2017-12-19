#!/usr/bin/python

from comlocal.core import Com
import time


def main():
	com = Com.Com(log=True)
	com.start()
	try:
		
		time.sleep(30)
	finally:
		com.stop()





if __name__ == "__main__":
	main()