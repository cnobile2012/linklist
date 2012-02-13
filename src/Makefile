#
# Makefile for Doubly Linked List API (Linux version)
#
# Copyright (c) 1996-2012 Carl J. Nobile
# Created: May 26, 1997
# Updated: 12/27/2011
#
# $Author$
# $Date$
# $Revision$
#
#
# Note on the copyright licenses.
# -------------------------------
# This Double Link List API is covered under either the Artistic or the
# Eclipse license. The Eclipse license is more business friendly so I
# have added it. Retaining the Artistic license prevents anybody that
# preferred it from complaining.
#
##########################################################################
# Copyright (c) 2007 Carl J. Nobile.
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
#
# Contributors:
#    Carl J. Nobile - initial API and implementation
##########################################################################
# Mac contributions to this Makefile by Charlie Buckeit
#
# To compile a shared version of libdll with test program execute:
#     make
# To compile a static version of libdll with test program execute:
#     make static
# To compile a debug shared version of libdll with test program execute:
#     make debug
# To compile the test program only using an installed shared library execute:
#     make test
#

include ../linklist.mk

AR	= ar rcs
CC	= gcc

DEBUG	= -g -DDEBUG
OFP	= -fomit-frame-pointer
SHARED	= -fPIC

# There should be no need to change anything below this line.
#--------------------------------------------------------------
PROG	= dll_main
TEST	= dll_test
SRCS	= $(PROG).c $(TEST).c
OBJS1	= $(PROG).o
OBJS2	= $(TEST).o

ifeq ($(OS),LINUX)
  FLIBNAME	= libdll.so.$(VERSION)
  MLIBNAME	= libdll.so.$(MAJORVERSION)
  LIBNAME	= libdll.so
  OPTIONS	= -O3 -ansi -pipe -fstrength-reduce -finline-functions -Wall \
		  -Wno-unused-result
  LDFLAGS	= -shared -Wl,-soname,$(MLIBNAME) -o $(FLIBNAME) $(OBJS1)
  THISLIB	= -L. -ldll
endif

ifeq ($(OS),MAC)
  FLIBNAME	= libdll.$(VERSION).dylib
  MLIBNAME	= libdll.$(MAJORVERSION).dylib
  LIBNAME	= libdll.dylib
  OPTIONS	= -O3 -ansi -fstrength-reduce -finline-functions -Wall
  LDFLAGS	= -dynamiclib -flat_namespace -current_version $(VERSION) \
		  -o $(FLIBNAME)  $(OBJS1) #\
#		  -install_name $(LIBDIR)/$(FLIBNAME)
  THISLIB	= -L. -ldll
endif

CFLAGS	= $(SHARED) $(OPTIONS) $(OFP) $(DEBUG)

#--------------------------------------------------------------
all	: 
	make libdll DEBUG=
	make $(TEST) DEBUG=

debug	:
	make libdll OFP=
	make $(TEST) OFP=

static	:
	make libdll.a SHARED= DEBUG=
	make $(TEST) SHARED= DEBUG=

debug-static :
	make libdll.a SHARED= OFP=
	make $(TEST) SHARED= OFP=

# Make the test program from the installed shared libraries.
test	:
	make $(TEST) DEBUG= THISLIB=-ldll

.c.o	: $(SRCS)
	$(CC) $(CFLAGS) -c $<

libdll	: $(OBJS1)
	$(CC) $(LDFLAGS)
	-ln -sf $(FLIBNAME) $(MLIBNAME)
	-ln -sf $(FLIBNAME) $(LIBNAME)

libdll.a: $(OBJS1)
	$(AR) $@ $(OBJS1)

$(TEST)	: $(OBJS2)
	$(CC) $(OBJS2) -o $(TEST) $(THISLIB)

$(PROG).o: $(PROG).c linklist.h
$(TEST).o: $(TEST).c linklist.h

#--------------------------------------------------------------
clean	:
	@rm -f *.o *~ *.bak \#*\# core test/*~ test/\#*\#

clobber	: clean
	@rm -rf libdll.* $(TEST) DLinklist.egg-info

distclean: clobber

install	: 
	cp ./libdll.so.$(VERSION) $(LIBDIR)
	cp ./linklist.h $(INCDIR)/linklist.h
	-(cd $(LIBDIR); ln -s $(FLIBNAME) $(MLIBNAME))
	-(cd $(LIBDIR); ln -s $(FLIBNAME) $(LIBNAME))
	/sbin/ldconfig

install-static:
	cp ./linklist.h $(INCDIR)/linklist.h
	cp ./libdll.a $(LIBDIR)/libdll.a

uninstall:
	rm -f $(LIBDIR)/libdll.* $(INCDIR)/linklist.h
