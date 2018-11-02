import urllib2,re
from queue import Queue
from threading import Thread

numberOfThreads = 4

class HeadRequest(urllib2.Request):
    def get_method(self):
        return "HEAD"

def headQuery(url):
    req = HeadRequest(url)
    try:
        response = urllib2.urlopen(req)
        response.close()
    except Exception as e:
        print e
        return False
    p=re.compile('Content-Length:\s(\d+)')
    if 'Accept-Ranges: bytes' in str(response.headers):
	s=re.search(p,str(response.headers))
	if s:return int(s.group(1))
    return False

def splitter(numBytes,threads):
    arr=[]
    n = int(numBytes/threads)
    for i in range(threads-1):
        arr.append(n)
    arr.append(numBytes-sum(arr))

def thread(url,startByte,endByte):
    #format as dictionaries like {'Range':'bytes=0-99999'} and return tuple of dictionaries
    #max of 1mb per byteRange

#???
class Downloader(Thread):
    def __init__(self, queue):
        Thread.__init__(self)
        self.queue = queue
    def run(self):
        while True:
            # Get the work from the queue and expand the tuple
            directory, link = self.queue.get()
            try:
                download_link(directory, link)
            finally:
                self.queue.task_done()

def fetcher(url,byteRange):
    req = urllib2.Request(url, headers=byteRange)
    #wrap below line in try-except a few times, if fails, throw error
    data = urllib2.urlopen(req).read()
    return data
    #collect data into arrays/dictionaries with keys as byterange/id

def writer():
    pass
