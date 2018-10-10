from fileslice import Slicer
import io
import time
import threading
import hashlib
import requests
from math import ceil
import time

def write(s, d, delay):
    data = s.read(5*2**20)
    while data:
        d.write(data)
        time.sleep(delay)
        data = s.read()

def copy(s, d):
    sf = open(s, 'br')
    df = open(d, 'bw')
    size = sf.seek(0, 2)
    sf.seek(0)
    
    ts = Slicer(sf)
    td = Slicer(df)
    
    sseg = []
    dseg = []
    threads = []
    
    segsize = size // 10
    
    start = 0
    while start < size:
        if start + segsize > size:
            segsize = size - start
        sseg.append(ts(start, segsize))
        dseg.append(td(start, segsize))
        start += segsize
    
    print('size:', size)
    print('source segments', len(sseg))
    print('destination segments', len(dseg))
    
    delay = 0.5
    for f, g in zip(sseg, dseg):
        threads.append(threading.Thread(target=write, args=(f, g, delay)))
        delay *= 1.3
        threads[-1].start()
    
    for c in threads:
        print('waiting for thread', c, '...', end='', flush=True)
        c.join()
        print('done')
        
    sf.close()
    df.close()
    
    sf = open(s, 'br')
    df = open(d, 'br')
    
    sc = hashlib.md5()
    dc = hashlib.md5()
    sc.update(sf.read())
    dc.update(df.read())
    sf.close()
    df.close()
    print(sc.hexdigest())
    print(dc.hexdigest())
    
def test():
    f = io.BytesIO()
    f.write(100*b'0123456789')
    
    tf = Slicer(f)
    with tf(5, 95) as t:
        t.seek(0)
        t.read(0)
        print(f.tell())
        print(t.read())
        print(f.tell())
        print(t.seek(-5, 2))
        print(t.read(0))
        print(f.tell())
    print(t.closed)

def dlrng(f, url, start, end=-1, barrier=None):
    if barrier is not None:
        barrier.wait()
    if end < 0:
        end = ''
        
    rng = 'bytes={}-{}'.format(start, end)
    r = requests.get(url, headers={'Range': rng}, stream=True)
    r.raise_for_status()
    for data in r.iter_content(128*2**10):
        f.write(data)
    
    f.close()

test()

exit()
url = 'http://localhost:8000/LCC.mp4'
r = requests.head(url, headers={'Range': 'bytes=0-'})
size = int(r.headers['Content-Length'])
for n in range(1, 4):
    print('n =', n, end=': ', flush=True)
    ev = threading.Event()
    
    f = open('test.mp4', 'bw')
    s = Slicer(f).slices(size, n)
    t = []
    for c in s:
        t.append(threading.Thread(target=dlrng, args=(c, url, c.start, c.end, ev)))
        t[-1].start()
    
    ev.set()
    t0 = time.time()
    for c in reversed(t):
        c.join()
    print(time.time()-t0)
    f.close()
    input()
