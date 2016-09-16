#!/usr/bin/python

"""

	logger management for VOGLbot

	writes out to both the console and a file 'voglbot.log'

"""

import sys
import logging
import time

logging.basicConfig(
	filename = 'ariadne.log',
	filemode = 'w',
	level=logging.DEBUG,
	format='%(asctime)s: %(message)s',
	datefmt = '%d-%m %H:%M:%S',
)
# for console logging
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)-12s : %(levelname)-8s %(message)s')
console.setFormatter(formatter)

logger = logging.getLogger()
logging.getLogger('').addHandler(console)
