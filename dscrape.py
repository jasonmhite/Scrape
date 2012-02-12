from daemon import Daemon
import feedparser
import urllib2
import ConfigParser
import string
import os, sys
from time import sleep
import Queue
import threading

class MyDaemon(Daemon):
    def loadqueue(self, configfile):
        self.defaults = {"zeropaddedq" : "true"}
        self.configfile = configfile
        self.q = Queue.Queue()
    def readconfig(self):
        self.currentable = []
        try:
            self.config = ConfigParser.SafeConfigParser(defaults)
            self.config.read(configfile)
        except:
            raise NameError('Config Parse Error')
        for sect in config.sections():
            searchstring = self.config.get(sect, 'sstring')
            episode = self.config.get(sect, 'currentepisode')
            url = self.config.get(sect, 'feedurl')
            feed = feedparser.parse(url)
            zeropaddedepnum = self.config.get(sect, "zeropaddedq")
            if zeropaddedepnum == 'true' and int(episode) < 10:
                episode = "0" + episode
            query = searchstring.replace("*EP", episode)
            self.currentable.append((sect,query,feed))
    def scan(self):
        
    def run(self):
        self.loadqueue()
        with open('testoutput.txt', 'w') as thefile:
            thefile.write('hello')
            sleep(10)

if __name__ == "__main__":
    daemon = MyDaemon('/tmp/daemon-example.pid')
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        else:
            print "Unknown command"
            sys.exit(2)
        sys.exit(0)
    else:
        print "usage: %s start|stop|restart" % sys.argv[0]
        sys.exit(2)
