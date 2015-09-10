# Doubly Linked List API Ver. 2.0.0

Copyright (c) 1996-2015  Carl J. Nobile
All rights reserved.

This program is free software; you can redistribute it and/or modify
it under the terms of either the Artistic or Eclipse Licenses.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
or FITNESS FOR A PARTICULAR PURPOSE.  See the Artistic License for more
details.

THE ACCOMPANYING PROGRAM IS PROVIDED UNDER THE TERMS OF THIS ECLIPSE PUBLIC LICE
NSE ("AGREEMENT"). ANY USE, REPRODUCTION OR DISTRIBUTION OF THE PROGRAM CONSTITU
TES RECIPIENT'S ACCEPTANCE OF THIS AGREEMENT.

--------------------------------------------------------------------------

## VERSION NUMBERS

I feel an explanation of how the version numbers for the package change is
important so we all know what to expect in future releases.  The major
number (1 at this time) changes when there is a paradigm shift in the way
the package works (See below TO-DO).  There could be incompatibilities
with code written using different major number versions.  The middle
revision number changes when important new features are added and the minor
version number changes generally for bug fixes and patches.  There should
be no incompatibilities between mid and minor version changes.

## COMPILATION

Not much to say here, the package is fairly easy to compile and use. Read
the docs for how to use the API.  The INSTALL file explains how to compile
and/or install/uninstall both the C and Python packages.

## LIBRARY USAGE

When new code is compiled it will link to libdll.so, and when a program
executes it will look for libdll.so.2.  This is why they are sym-linked
to libdll.so.2.0.0 the current version.

## TO-DO

The major version will change with the following code changes.  At present
the linklist defaults to doing memory allocations for each node created. This
is wasteful of resources and time consuming.  It is my hope to create a
mechanism to allow larger blocks of memory to be allocated which can be
changed on the fly.  This should substantially speed up operations.

There is a fully thread safe version in the works, but I have been putting it
off for some years now. If ever I decide that it is something that people
really want I may continue with it, but for now it will stay in a maybe-will-do
state.

## WEB SITE

Yes I have a WIKI for this and my other projects at:

http://wiki.tetrasys-design.net/

The above URL is my personal page where links to the Doubly Link List can
be found.

EMAIL

Carl J. Nobile <carl.nobile@gmail.com>
