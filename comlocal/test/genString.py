#!/usr/bin/python

import string
import random
import argparse

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument ("-n", "--number", required = True, help="number of characters in string")
	args = parser.parse_args()

	print ''.join(random.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits) for _ in range(int(args.number)))


if __name__ == '__main__':
	main()
