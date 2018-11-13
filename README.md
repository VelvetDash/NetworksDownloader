# Networks Downloader
50.012 Networks Project

## Project Topic
Multi-threaded downloader

## Project Description
Create a multi-threaded downloader for parallel data downloading (as a service to browsers, for example), 
that would download data in parallel data and merge in proper order before passing to the browser.

## Implementation

## Testing

## How to Run
Download the zip file and extract it.


Open `downloader.py`, some of the initial variables could be modified.
```python
# initialization
numberOfThreads = 4
dataDict={}

url = 'https://i.redd.it/9orb8me3xpv11.jpg'
```


`numberOfThreads` is the number of threads used for the downloader. The default value is `4`.


`url` is the link of file you want to download. There are three urls provided in the code for testing.


<br>Then run `downloader.py`. The file will be saved to the folder of where `downloader.py` stored.
