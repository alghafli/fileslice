'''
:Date: 2018-10-10
:Version: 0.0.1
:Authors:
    - Mohammad Alghafli <thebsom@gmail.com>

File slice is a part of a file. This library allows you to open a binary file
and see only part of it. You specify the start and end of the file part you want
to see. Read and write operations will always start at the specified start
position and will never exceed the specified end position. Here is an example of
how to use it::
    
    from fileslice import Slicer
    
    #let's open a file for reading
    r = open('example.png', 'br')
    
    #create a slicer for the file
    slicer = Slicer(r)
    
    #the slicer behaves like a function. call it to create as many fileslices
    #as you want
    start = 5   #the beginning of our partial file is at 5
    size = 95   #the size of the part is 95 bytes so our end is 99
    fileslice = slicer (start, size)     #this is a file like object
    
    #now we have a fileslice file from byte 5 to byte 99.
    #the initial partial file seek position is 0.
    print(fileslice.read())  #will print from byte 5 to 99.
    
    #now our seek position is at the end of the fileslice file
    #that is byte 100 of the full file
    try:
        #if we seek to a position out of the fileslice file range (from 0 to 95)
        fileslice.seek(200)
    except ValueError:
        #an exception will be thrown
        print('error while seeking to 200')
    
    #we can seek from the end of the fileslice or from current fileslice
    #seek position
    #let's seek to fifth byte from the end of the file. that is byte 95
    fileslice.seek(-5, 2)

This library also works in writable files. Multiple threads can be used to read
and write to different file slices from the same file. Just make sure you do not
use the original opened file or the fileslices (and the original file object)
will be confused.
'''

from io import SEEK_SET, SEEK_CUR, SEEK_END
from threading import RLock
import math
import re

__version__ = re.search(
        ':Version: (?P<version>[0-9](\.[0-9])*)',
        __doc__
    ).group(1)

class Slicer:
    '''
    File slicer. Use this class to slice a file into multiple file slices and
    use each slice as if it was an independant file.
    '''
    def __init__(self, f):
        '''
        args:
            * f (file-like object): the file to slice.
        '''
        self.f = f
        self.lock = RLock()
    
    def slices(self, size, n=3):
        '''
        Create equal sized slices of the file. The last slice may be larger than
        the others.
        
        args:
            * size (int): The full size to be sliced.
            * n (int): The number of slices to return.
        returns:
            A list of `FileSlice` objects of length (n).
        '''
        if n <= 0:
            raise ValueError('n must be greater than 0')
        if size < n:
            raise ValueError('size argument cannot be less than n argument')
        slice_size = size // n
        last_slice_size = size - (n-1) * slice_size
        t = [self(c, slice_size) for c in range(0, (n-1)*slice_size, slice_size)]
        t.append(self((n-1)*slice_size, last_slice_size))
        return t
    
    def __call__(self, start, size):
        '''
        Create a file slice.
        args:
            * start (int): The beginning position of the slice. The slice will
                read/write to this position when it is seeked to 0.
            * size (int): The size of the slice.
        '''
        
        return FileSlice(self.f, start, size, self.lock)

class FileSlice:
    '''
    .. note:: The `Slicer` class is a convinient way to create instances of this
        class.
    
    A file slice. An instance of this class is a file-like object that only
    looks at a specific region in the original file object. Multiple slices can
    be created from the same file object and each slice will have its own seek
    position and you can read and write to each slice independantly. `FileSlice`
    instances generated from the same `Slicer` object are thread-safe.
    
    In addition to the class methods, the following methods call the methods
    with the same name from the original file object:
    
        * readable.
        * writable.
        * seekable.
        * isatty.
        * fileno.
    '''
    __relayed_props__ = (
            'readable',
            'writable',
            'seekable',
            'isatty',
            'fileno',
        )
    
    def __init__(self, f, start, size, lock):
        '''
        args:
            * f (file-like object): file to slice.
            * start (int): The beginning position of the slice.
            * size (int): The size of the slice.
            * lock (threading.Lock): File lock to prevent multiple access from
                different slices in different threads.
        '''
        self.f = f
        self.start = start
        self.size = size
        self.pos = 0
        self.lock = lock
        self.closed = f.closed
    
    @property
    def end(self):
        '''
        The end position of the slice. The slice will not read or write if the
        new position is ahead of this value.
        '''
        return self.start + self.size - 1
    
    def tell(self):
        '''
        Same as `file.tell()` but for the slice. Returns a value between
        `self.start` and `self.size` inclusive.
        '''
        if self.closed:
            raise ValueError('I/O operation on closed file.')
        return self.pos
    
    def seek(self, offset, whence=0):
        '''
        Same as `file.seek()` but for the slice. Returns a value between
        `self.start` and `self.size` inclusive.
        
        raises:
            ValueError if the new seek position is not between 0 and
            `self.size`.
        '''
        if self.closed:
            raise ValueError('I/O operation on closed file.')
        
        if whence == SEEK_SET:
            pos = offset
        elif whence == SEEK_CUR:
            pos = self.pos + offset
        elif whence == SEEK_END:
            pos = self.size + offset
        
        if not 0 <= pos <= self.size:
            raise ValueError('new position ({}) will fall outside the file slice range (0-{})'.format(pos, self.size))
        
        self.pos = pos
        return self.pos
    
    def read(self, size=-1):
        '''
        Same as `file.read()` but for the slice. Does not read beyond
        `self.end`.
        '''
        if self.closed:
            raise ValueError('I/O operation on closed file.')
        
        if size == -1 or size > self.size - self.pos:
            size = self.size - self.pos
        
        with self.lock:
            self.f.seek(self.start + self.pos)
            result = self.f.read(size)
            self.seek(self.pos + size)
        
        return result
    
    def write(self, b):
        '''
        Same as `file.write()` but for the slice.
        
        raises:
            EOFError if the new seek position is > `self.size`.
        '''
        if self.closed:
            raise ValueError('I/O operation on closed file.')
        
        if self.pos + len(b) > self.size:
            raise EOFError('new position ({}) will fall outside the file slice range (0-{})'.format(self.pos + len(b), self.size))
        
        with self.lock:
            self.f.seek(self.start + self.pos)
            result = self.f.write(b)
            self.seek(self.pos + len(b))
        
        return result
    
    def writelines(self, lines):
        '''
        Same as `file.writelines()` but for the slice.
        
        raises:
            EOFError if the new seek position is > `self.size`.
        '''
        lines = b''.join(lines)
        self.write(lines)
    
    def close(self):
        '''
        Same as `file.close()` but for the slice. All file access operations
        will raise ValueError after the file is closed. The original file object
        is not closed.
        '''
        with self.lock:
            self.closed = True
    
    def flush(self):
        '''
        Flushes the original file.
        '''
        with self.lock:
            return self.f.flush()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        '''
        Only closes the slice. The original file is not closed.
        '''
        self.close()
        return False
    
    def __getattr__(self, name):
        if name in self.__relayed_props__:
            getattr(self.f, name)
        else:
            raise AttributeError("{} object has no attribute '{}'".format(type(self).__name__, name))

