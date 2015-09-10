# Installation of the Doubly Linked List

Installing on Windows
---------------------
You are pretty much on your own here. The package contains a makefile for
an old verson of the windows compiler. If you can write a more uptodate
one, please submit it to me. The old makefile is: ms60dll.mak. Also a patch
for the Python ctypes library would be appreciated.

Installing on Windows Cygwin
----------------------------
This also has not been tested in a very long time. The makefile is: djgppdll.mak
If you can improve on it please contact me.

Installing Python API on Linux
------------------------------
The Python API is new as of version 2.0.0 it can be install by running
$ sudo easy_install linklist-2.0.0.tar.gz
or
$ cd linklist-2.0.0
$ make egg
$ sudo easy_install dist/DLinklist*.egg

Installing C API on Linux
-------------------------
To install use tar to extract the files into the directory where you
want it to reside.  Usually in /usr/local/src.

$ tar -xvzf linklist-2.0.0.tar.gz -C /your/path

The above tar command only works with GNU tar.  If you don't have this
tar try:

$ cp linklist-2.0.0.tar.gz /your/path
$ cd /your/path
$ gzcat linklist-2.0.0.tar.gz | tar xvf -

Next cd to the linklist.x.x.x directory and type one of the following,
assuming you're using the GNU compiler:

$ make            creates a shared library and Python egg file
or
$ make static     creates a static library
or
$ make egg        creates only the Python egg file.

Read the Makefile for further compilation options.

To install the library in the /usr/local/lib directory enter either
make install or make install-static.  To install the docs enter
make install-docs.  The default directory is /usr/docs/linklist.x.x.x.
Edit the Makefile if you want a different directories.

NOTES:

1) IMPORTANT -- If you do not change the PREFIX environment in the linklist.mk
   the libraries and the header file will be put into /usr/local/... This
   means that when The Makefile runs ldconfig it may not actually do anything
   unless you have put /usr/local/lib in your /etc/ld.so.conf.d/ directory. I
   generally just make a file named local.conf with /usr/local/lib in it. Older
   systems just put everything in the /etc/ld.so.conf file itself.

2) If you have an old version of the library installed the test program
   (dll_test) will pull that library in when shared objects are used.  If
   you want to test the new library use the demo.sh script instead of running
   the test program directly.  The script will set the environment correctly.

3) The makefiles for the djgpp and MS6.0 compilers have not been tested for
   years.  I doubt if they work any more and none of the new stuff has been
   added to them.  I've left them in the distribution for those daring soles
   who might want to use them.

4) If you try to build the Python epydoc files remove any old install of the
   linklist egg file first or you may run into issues where the things do not
   get built correctly.

The documentation is now much more complete.  This distribution now provides a
postscript, pdf, html, and Python epydoc versions of the documentation.

If you have any problems, please contact me at:

carl.nobile@gmail.com

wiki.tetrasys-design.net
