#!/bin/bash
../test/sendDataToDummy.py -m '{"msg":"hello","dest":1}' -c 100 &
coverage run -m unittest discover -s tests/