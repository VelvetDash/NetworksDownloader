import urllib2,re
import Queue
##from threading import Thread
from multiprocessing.dummy import Pool as ThreadPool

numberOfThreads = 4
url='https://i.redd.it/9orb8me3xpv11.jpg'

class HeadRequest(urllib2.Request):
    def get_method(self):
        return "HEAD"

def headQuery(url=url):
    req = HeadRequest(url)
    try:
        response = urllib2.urlopen(req)
        response.close()
    except Exception as e:
        print e
        return False
    try: return int(response.headers['Content-Length'])
    except: return False

#example: headQuery('https://i.redd.it/5wyehherasv11.jpg')

def splitter(numBytes,threads=numberOfThreads):
    arr,arrOfTuples=[],[]
    n = int(numBytes/threads)
    for i in range(threads-1):
        arr.append(n)
    arr.append(numBytes-sum(arr))
    for i in range(threads-1,-1,-1):
        arr[i]+=sum(arr[:i])
    start=0
    for i in range(threads):
        arrOfTuples.append((start,arr[i]))
        start=arr[i]+1
    return arrOfTuples

#example: splitter(12345678,4)

def thread(url,startByte,endByte):
    #format as dictionaries like {'Range':'bytes=0-99999'} and return tuple of dictionaries
    #max of 1mb per byteRange
    
    if (endByte - startByte) > 1*1024*1024:
        print "ByteRange should be within a maximum of 1 MB"
        return False
    
    req = urllib2.Request(url)
    req.headers['Range'] = 'bytes=%s-%s' % (startByte, endByte)
    #wrap below line in try-except a few times, if fails, throw error
    data = urllib2.urlopen(req).read()
    #return data
    dataDict[startByte]=data
    #collect data into arrays/dictionaries with keys as byterange/id

#splits the arg into its components
#threadcaller(args) -> thread(args[0],args[1],args[2])
threadcaller = lambda args: thread(url, args[0], args[1])

byteSize = headQuery()
if byteSize and byteSize>0:
    args=splitter(byteSize)
else:
    raise Exception('cannot get number of bytes of the file in that URL')


dataDict={}
#example byte ranges
##data[0]=thread(url,0,199999)
##data[200000]=thread(url,200000,399999)
##data[400000]=thread(url,400000,599999)
##data[600000]=thread(url,600000,745899)

pool = ThreadPool(numberOfThreads) 
results = pool.map(threadcaller, args)
pool.close()
pool.join()

import os
def writer():
    fn=re.compile('([^/]+\.\w+$)')
    result=re.search(fn,url)
    if result:
        filename=result.group(1)
    else:
        filename='file.txt'
    while(os.path.exists(filename)):
        parts=filename.split('.')
        filename=parts[0]+'_1'+'.'+parts[1]
    sortedKeys=sorted(dataDict.keys())
    with open(filename,'wb') as f:
        for i in sortedKeys:
            f.write(dataDict[i])
    print('{} saved at this script\'s folder'.format(filename))
