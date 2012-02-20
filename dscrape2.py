from daemon import Daemon
import feedparser
import urllib2
import ConfigParser
import string
import os, sys
from time import sleep
import Queue
import threading
import transmissionrpc
import glob
import syslog

class MyDaemon(Daemon):

    def __init__(self, configfile, pidfile, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.pidfile = pidfile
        self.configfile = configfile
        self.directory = '/Users/jmhite/Anime Weekly/'
        self.q = Queue.Queue(0)
        self.updateq = Queue.Queue(0)
        syslog.openlog("dscrape")
#       self.tlock = threading.Lock()

    def run(self):
        self.check_new()
        for i in range(1, max([4, self.q.qsize()])):
            self.Worker(self.q, self.updateq).start()
        while threading.activeCount() > 1:
            sleep(1)
        self.update()
        self.signal_transmission()

    def check_new(self):
        defaults = {"zeropaddedq" : "true"}
        try:
            config = ConfigParser.SafeConfigParser(defaults)
            config.read(self.configfile)
        except:
            syslog.syslog(syslog.LOG_ALERT, 'Config Parse Error')

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

    def update(self):
        try:
            newconfig = ConfigParser.SafeConfigParser()
            newconfig.read(self.configfile)
                
            while not self.updateq.empty():
                uit = self.updateq.get()
                self.testvar.append(uit)
                i = int(newconfig.get(uit, "currentepisode")) + 1
                newconfig.set(uit, "currentepisode", str(i))
            with open(self.configfile, "wb") as updated:
                newconfig.write(updated)
        except:
            syslog.syslog(syslog.LOG_ALERT, 'Config Write Error')
        
    def signal_transmission(self):
        try:
            tc = transmissionrpc.Client('localhost', port=9091)
            for inf in glob.glob(os.path.join(self.directory, "*.torrent")):
                try:
                    tc.add_uri(inf, paused=True)
                    sleep(2)
                    os.remove(inf)
                except:
                    pass
        except:
            pass

    class Worker(threading.Thread): 

        def __init__(self, inqueue, outqueue):
            self.inqueue = inqueue
            self.outqueue = outqueue
            threading.Thread.__init__(self)

        def run(self):
            while not self.inqueue.empty():
                entry = self.inqueue.get()
                try:
                    dl = urllib2.urlopen(entry[ 2 ], timeout=2)
                    with open(self.directory + entry[1] + '.torrent', 'w') as outfile:
                        outfile.write(dl.read())
                    self.outqueue.put(entry[0])
                    self.inqueue.task_done
                except:
                    syslog.syslog(syslog.LOG_ALERT, 'Download Error')

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
