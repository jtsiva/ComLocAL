#!/usr/bin/python

from comlocal.core import Com
import time


def main():
	com = Com.Com()
	try:
		com.start()
		time.sleep(30)
	finally:
		com.stop()





if __name__ == "__main__":
	main()