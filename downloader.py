import urllib2,re
import Queue
from threading import Thread
##from multiprocessing.dummy import Pool as ThreadPool

numberOfThreads = 4
url='https://i.redd.it/9orb8me3xpv11.jpg'         #image file
##url='https://www.w3.org/TR/PNG/iso_8859-1.txt'    #text file
##url='http://vis-www.cs.umass.edu/lfw/lfw-a.zip'   #large file
dataDict={}

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

def thread(startByte,endByte):
    #format as dictionaries like {'Range':'bytes=0-999999'} and return tuple of dictionaries
    #https://www.google.com/search?q=python+optimal+file+chunk+size
    req = urllib2.Request(url)
    req.headers['Range'] = 'bytes=%s-%s' % (startByte, endByte)
    data = urllib2.urlopen(req)
    s=startByte
    while endByte>s+1024**2:
        dataDict[s]=data.read(1024**2)
        s+=1024**2
    dataDict[s]=data.read(endByte-s +1)
    data.close()

byteSize = headQuery()
if byteSize and byteSize>0:
    args=splitter(byteSize)
else:
    raise Exception('cannot get number of bytes of the file in that URL')


threadPool=[]
for i in range(numberOfThreads):
    threadPool.append(Thread(name='thread'+str(i), target=thread, args=args[i]))
for t in threadPool:
    t.start()
for t in threadPool:
    t.join()


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

writer()
