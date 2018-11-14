# Networks Downloader
50.012 Networks Project

## Project Topic
Multi-threaded downloader

## Project Description
Create a multi-threaded downloader for parallel data downloading (as a service to browsers, for example), that would download data in parallel data and merge in proper order before passing to the browser.

## Implementation
### Header Extraction
We use `urllib2` to request the header of target url. In the header, there are two values that we are interested:


`Content-Length`: Length of data stream, which is going to be split into trunks for multiple threads.


`Accept-Range`: We use this value to confirm that the server accept partial byte ranges, so each thread can request different byte ranges.


### Splitting
With length of data that will be downloaded, we then split those bytes into threads.


The function `splitter` returns an array of threads. Each element in the array is a tuple of start index and end index for one thread. For example:
```
[(0, 186474), (186475, 372948), (372949, 559422), (559423, 745899)]
```
The tuple is used to decide which part of the data is downloaded by this thread.


### Thread creation
We then created several threads. Each thread's callable object is set to be the function for single thread downloading, and result of splitting is used as the arguments for the callable function.
```python
args = splitter(byteSize, numberOfThreads)
```
```python
threadPool = []
for i in range(numberOfThreads):
    threadPool.append(Thread(name='thread' + str(i), target=thread, args=args[i])
```


The threads can be activated by the `start()` methods.


### Downloading
For each thread, we get the data using `urllib2.urlopen`. The optimal chunk size is set to be 1MB. Data are downloaded in chunks and stored to data dictionary. The format of items in data dictionary is:
```
{[start index]: [data fragment downloaded]}
```


### Merging
After finish segment downloading, we sort the dictionary so that the data fragments are in the correct order. Then for each key, we write the segments to the output file.


## Testing
### checker
### fixer


## How to Run
Download the zip file and extract it.

Open command prompt (or terminal for UNIX system), `cd` to the folder `NetworksDownloader`, where you could find `downloader.py`.


Make sure you are using **python2** to run the program.


Run the command `python downloader.py -n [number of threads] -i [link of file you want to download]`.


For example, `python downloader.py -n 4 -i https://i.redd.it/9orb8me3xpv11.jpg`


We have provided three example urls for testing:
```
url = 'https://i.redd.it/9orb8me3xpv11.jpg'         # image file
url = 'https://www.w3.org/TR/PNG/iso_8859-1.txt'    # text file
url = 'http://vis-www.cs.umass.edu/lfw/lfw-a.zip'  # large file
```


After running the command, the details of downloading will be displayed, and the file will be saved to the folder of current directory.


```
(base) C:\Users\User\Desktop\NetworksDownloader>python downloader.py -n 4 -i https://i.redd.it/9orb8me3xpv11.jpg
----------downloader----------------
Number of Threads:     4
Input URL:             https://i.redd.it/9orb8me3xpv11.jpg
Data Size:             745899

Start multi-thread downloading...

File saved at C:\Users\User\Desktop\NetworksDownloader\9orb8me3xpv11.jpg

Finish downloading in 1.87400007248 seconds
```
