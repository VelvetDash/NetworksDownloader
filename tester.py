import urllib2,re,os
#import Queue
from threading import Thread
from time import time

#numberOfThreads = 4
#url='https://i.redd.it/9orb8me3xpv11.jpg'         #image file
###url='https://www.w3.org/TR/PNG/iso_8859-1.txt'    #text file
###url='http://vis-www.cs.umass.edu/lfw/lfw-a.zip'   #large file
#dataDict={}


class HeadRequest(urllib2.Request):
    def get_method(self):
        return "HEAD"

# request and return length of content
def headQuery(url):
    #gets number of bytes of the file at url
    req = HeadRequest(url)
    try:
        response = urllib2.urlopen(req)
        response.close()
    except Exception as e:
        print(e)
        return False
    try: return int(response.headers['Content-Length'])
    except: return False


# split bytes into 'threads' number of ranges
def splitter(numBytes,threads):
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


#
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

# checks whether there are overlaps/ missing data/ excess data
def checker():
    keys=[]
    length=0
    for k,v in dataDict.iteritems():
        keys.append(k)
        length+=len(v)
    for start in keys:
        end=start+len(dataDict[start])-1
        if end>=byteSize:
            print('byte range exceeded\nend:{} byteSize:{}'.format(end,byteSize))
            return False
        for i in keys:
            #print('start:{} end:{} i:{}'.format(start,end,i)) #for debug
            if i>start and i<=end:
                print('overlap detected\nstart:{} end:{} i:{}'.format(start,end,i))
                return False
    if length!=byteSize:
        print('length difference\nlength:{} byteSize:{}'.format(length,byteSize))
        return False
    return True


# in-place fixes for problems detected by checker()
def fixer():
    if not 0 in dataDict: dataDict[0]=""
    keys=sorted(dataDict.iterkeys(),reverse=True)
    cutoff=byteSize
    for k in keys:
        #fix overlaps/ excess data
        if k+len(dataDict[k])>cutoff:
            truncBytes=dataDict[k][:cutoff-k-len(dataDict[k])]
            dataDict[k]=truncBytes
        #fix missing data
        if k+len(dataDict[k])<cutoff:
            req = urllib2.Request(url)
            print('requesting bytes:{}-{}'.format(k+len(dataDict[k]), cutoff-1))
            req.headers['Range'] = 'bytes=%s-%s' % (k+len(dataDict[k]), cutoff-1)
            data = urllib2.urlopen(req)
            dataDict[k+len(dataDict[k])]=data.read()
        cutoff=k
    
# returns a file name that is available
def getFileName():
    fn=re.compile('([^/]+\.[^/]+$)')
    result=re.search(fn,url)
    if result:
        filename=result.group(1)
    else:
        filename='file.txt'
    while(os.path.exists(filename)):
        parts=filename.split('.')
        filename=parts[0]+'_1'+'.'+parts[1]
    return filename


# writes data to file
def writer():
    filename=getFileName()
    sortedKeys=sorted(dataDict.keys())
    with open(filename,'wb') as f:
        for i in sortedKeys:
            f.write(dataDict[i])
    sep = '\\' if os.name=='nt' else '/'
    print('File saved at {}{}{}'.format(os.getcwd(),sep,filename))





if __name__ == '__main__':
    
    # initialization
    numberOfThreads = 4
    dataDict={}

    ##url = 'https://i.redd.it/9orb8me3xpv11.jpg'         #image file
    ##url = 'https://www.w3.org/TR/PNG/iso_8859-1.txt'    #text file
    url = 'http://vis-www.cs.umass.edu/lfw/lfw-a.zip'   #large file
    
    byteSize = headQuery(url)
    print 'data size: '+str(byteSize)
    
    if byteSize and byteSize>0:
        args=splitter(byteSize,numberOfThreads)
    else:
        raise Exception('cannot get number of bytes of the file in that URL')
    
    
    threadPool=[]
    for i in range(numberOfThreads):
        threadPool.append(Thread(name='thread'+str(i), target=thread, args=args[i]))
        #print 'thread'+str(i)+' byte range: '+str(args[i])
        
    for t in threadPool:
        t.start()
    for t in threadPool:
        t.join()
    while not checker():
        fixer()

    keys=dataDict.keys()
    print ('test case 1: missing data at middle')
    r=keys[2]
    dataDict[r]=dataDict[r][:-5]
    try:
        assert not checker()
        fixer()
        assert checker()
        print ('test case 1 passed\n')
    except AssertionError:
        print ('test case 1 failed\n')

    print ('test case 2: excess data at middle')
    dataDict[r]=dataDict[r]+dataDict[r][:2]
    try:
        assert not checker()
        fixer()
        assert checker()
        print ('test case 2 passed\n')
    except AssertionError:
        print ('test case 2 failed\n')

    print ('test case 3: excess data at end')
    r=max(keys)
    dataDict[r]=dataDict[r]+dataDict[r][:3]
    try:
        assert not checker()
        fixer()
        assert checker()
        print ('test case 3 passed\n')
    except AssertionError:
        print ('test case 3 failed\n')

    print ('test case 4: missing data at end')
    dataDict[r]=dataDict[r][:-4]
    try:
        assert not checker()
        fixer()
        assert checker()
        print ('test case 4 passed\n')
    except AssertionError:
        print ('test case 4 failed\n')

    print ('test case 5: missing data at start')
    r=min(keys)
    dataDict[r+2]=dataDict[r][2:]
    del dataDict[r]
    try:
        assert not checker()
        fixer()
        assert checker()
        print ('test case 5 passed\n')
    except AssertionError:
        print ('test case 5 failed\n')

    print ('test case 6: missing data at middle and excess data at end')
    r=keys[2]
    dataDict[r]=dataDict[r][:-6]
    r=max(keys)
    dataDict[r]=dataDict[r]+dataDict[r][:6]
    try:
        assert not checker()
        fixer()
        assert checker()
        print ('test case 6 passed\n')
    except AssertionError:
        print ('test case 6 failed\n')

    print ('test case 7: excess data at middle and missing data at end')
    dataDict[r]=dataDict[r][:-7]
    r=keys[2]
    dataDict[r]=dataDict[r]+dataDict[r][:7]
    try:
        assert not checker()
        fixer()
        assert checker()
        print ('test case 7 passed\n')
    except AssertionError:
        print ('test case 7 failed\n')
    
    writer()
    
