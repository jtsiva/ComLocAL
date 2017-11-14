#!/usr/bin/python

from comlocal.core import Com
import time

def main():
	com = Com.Com()
	com.start()
	time.sleep(30)
	com.stop()





if __name__ == "__main__":
	main()