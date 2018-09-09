from urllib.request import urlopen
import time
import os

def download(url,name=None):
    if name != None:
        filename = name
    else:
        filename = url.split('/')[-1]
    filename = os.path.join("images",filename)
    if os.path.isfile(filename) == False:
        img_file = open(filename, "wb")
        img_file.write(urlopen(url).read())
        img_file.close()
        absolute_path = os.path.dirname(os.path.abspath(filename))
        return filename, absolute_path
    else:
        print("File already exists")
        absolute_path = os.path.dirname(os.path.abspath(filename))
        return filename, absolute_path




oldTime = time.time()
im = download("http://i.imgur.com/dy1sL1N.png","test2.png")
print(im)
print("Download time:",time.time()-oldTime)
