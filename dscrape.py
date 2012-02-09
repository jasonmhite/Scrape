from daemon import daemon
import feedparser
import urllib2
import ConfigParser
import string
import os
from time import sleep

class MyDaemon(Daemon)
	def __init__(self, configfile):
		self.defaults = {"zeropaddedq" : "true"}
		self.configfile = configfile

	
