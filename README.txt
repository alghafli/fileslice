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

    --------
    Tutorial
    --------
    Check out fileslice tutorial at http://fileslice.readthedocs.io/
    
