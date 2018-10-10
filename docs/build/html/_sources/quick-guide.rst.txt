===========
Quick Guide
===========

-------------
Usage example
-------------

This is a typical usage example::
    
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
    #let's seek to fifth byte from the end of the fileslice. that is byte 95
    fileslice.seek(-5, 2)

---------------------
Equally sized splices
---------------------

::

    from fileslice import Slicer
    
    #let's open a file for reading
    r = open('example.png', 'bw')
    
    #create a slicer for the file
    slicer = Slicer(r)
    
    #slicer.slices(<total size>, <number of slices>)
    #returns a list of file slices
    #each slice will be 250 bytes
    slice_list = slicer.slices(1000, 4)
    
    #if you used:
    #slice_list = slicer.slices(1000, 3)
    #the first two slices will be 332. the last slice will be 334
    #the last slice can be larger than the rest in some cases like this one

----------------
Further readings
----------------

In :doc:`reference` you will find the library reference.

