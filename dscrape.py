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
        self.lock = threading.Lock()

    def update(self):
        self.currentable = []
        with self.lock:
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
            for entry in self.currenttable:
                hit = self.scan_query(entry)
            if hit:
                self.q.put(hit)
               
    def scan_query(self,item):
        res = False
        for entry in item[2].entries:
            title = filter(lambda x: x in string.printable, entry.title)
            if item[1] in title:
                res = (nib[0], nib[1], entry.link)
            return(res)
        return(res)

    def run(self):
        self.loadqueue()
        with open('testoutput.txt', 'w') as thefile:
            thefile.write('hello')
            sleep(10)

    class Worker(threading.Thread): 
        def __init__(self, queue, configfile):
            self.__queue = queue
            self.plock = lock
            self.configfile = configfile
            self.matches = []
            threading.Thread.__init__(self)

        def download(self, item):
            try:
                dl = urllib2.urlopen(item[2], timeout=2)
                with open("/Users/jmhite/Automatically Downloaded/" + item[1] + '.torrent', 'w') as outfile:
                    outfile.write(dl.read())
                self.matches.append(item)
            except:
                raise NameError('Download Error')
        
        def update(self):
            with self.plock:
                try:
                    newconfig = ConfigParser.SafeConfigParser()
                    newconfig.read(configfile)
       
                for m in matchlist:
                    i = int(newconfig.get(m[0], "currentepisode")) + 1
                    newconfig.set(m[0], "currentepisode", str(i))
                with open(configfile, "wb") as updated:
                    newconfig.write(updated)
                except:
                    raise NameError('Config Replace Error')

        def run(self):
            while True:
                if queue.empty():
                    self.update(self.matches)
                    break
                item = self.__queue.get()
                try:
                    queue.task_done()



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
