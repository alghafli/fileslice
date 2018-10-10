==================
fileslice Tutorial
==================

This tutorial gives an introduction to how to use fileslice python library and its
features.

This is not a python tutorial. You are expected to have general knowledge in
python before you start this tutorial.

-----------
The problem
-----------

Usually, programs open a file and look at it as a whole. However, it happens sometimes that your program needs to look at part of the file and never look at
other parts of the file. For example, in a download manager, you may want to
start multiple download threads, each thread downloads part of the file. In file
servers, if the client requests part of the file, the server will open only the
requested part of the file.

------------
The solution
------------

This library allows you to open part of a file. The part you open behaves like a
regular independant file. Multiple parts of a file can be opened simultaneously. You can read or write to each part from multiple threads at the same time.
Seeking to the beginning of a part is does not affect the seek position of other
parts since each part has its own seek position and the library takes care of
thread safety.

-------
Content
-------

.. toctree::
    :maxdepth: 2

    installation
    quick-guide
    reference
   

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

