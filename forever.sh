#!/usr/bin/env python3

from subprocess import Popen
import sys

filename = sys.argv[1]
while True:
    print("Starting " + filename)
    p = Popen("python " + filename, shell=True)
    p.wait()
