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

    def __init__(self, configfile, pidfile, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.pidfile = pidfile
        self.configfile = configfile
        self.q = Queue.Queue(0)
        self.updateq = Queue.Queue(0)
        self.tlock = threading.Lock()
        self.testvar = []

    def run(self):
        self.check_new()
        self.download()
        self.update()
        self.test()

    def check_new(self):
        defaults = {"zeropaddedq" : "true"}
        try:
            config = ConfigParser.SafeConfigParser(defaults)
            config.read(self.configfile)
        except:
            raise NameError('Config Parse Error')

        table = []
        for sect in config.sections():
            searchstring = config.get(sect, 'sstring')
            episode = config.get(sect, 'currentepisode')
            url = config.get(sect, 'feedurl')
            feed = feedparser.parse(url)
            zeropaddedepnum = config.get(sect, "zeropaddedq")
            if zeropaddedepnum == 'true' and int(episode) < 10:
                episode = "0" + episode
            query = searchstring.replace("*EP", episode)
            table.append((sect,query,feed))

        for entry in table:
            hit = self.scan_query(entry)
            if hit:
                self.q.put(hit)

    def scan_query(self, nib):
        res = False
        for entry in nib[2].entries:
            title = filter(lambda x: x in string.printable, entry.title)
            if nib[1] in title:
                res = (nib[0], nib[1], entry.link)
            return(res)
        return(res)

    def download(self):
        while not self.q.empty():
            entry = self.q.get()
            try:
                dl = urllib2.urlopen(entry[ 2 ], timeout=2)
                with open("/Users/jmhite/Desktop/" + entry[1] + '.torrent', 'w') as outfile:
                    outfile.write(dl.read())
                self.updateq.put(entry[0])
            except:
                raise NameError('Download Error')
            self.q.task_done()

    def update(self):
        try:
            newconfig = ConfigParser.SafeConfigParser()
            newconfig.read(self.configfile)
            with open("/Users/jmhite/Desktop/test2.txt", 'w') as thefile:
                thefile.write("success")
                
            while not self.updateq.empty():
                uit = self.updateq.get()
                self.testvar.append(uit)
                i = int(newconfig.get(uit, "currentepisode")) + 1
                newconfig.set(uit, "currentepisode", str(i))
            with open(self.configfile, "wb") as updated:
                newconfig.write(updated)
        except:
            raise NameError('Config Replace Error')
        

    def test(self):
        with open("/Users/jmhite/Desktop/text.txt",'w') as thefile:
            thefile.write("Test \n")
            thefile.write(str(self.configfile) + "\n")
            self.testvar.append('blank')
            for i in self.testvar:
                thefile.write(str(i) + "\n")

if __name__ == "__main__":
    daemon = MyDaemon('/Users/jmhite/github/local/Scrape/list.cfg','/tmp/daemon-example.pid')

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
