#
# Makefile for Doubly Linked List API (Linux version)
#
# Copyright (c) 1996-1998 Carl J. Nobile
# Created: May 26, 1997
# Updated: 07/05/99
#
# $Author$
# $Date$
# $Revision$
#
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
AR	= ar rcs
CC	= gcc

ERRFILE	= {$*}.err
DEBUG	= -g -DDEBUG
OFP	= -fomit-frame-pointer
SHARED	= -fPIC
OPTIONS	= -O3 -m486 -ansi -pipe -fstrength-reduce -finline-functions -Wall

# The options below should be used instead of the above on the Mac
#OPTIONS	= -O3 -fstrength-reduce -finline-functions -Wall

# Change the directory paths below to reflect your system
LIBDIR	= /usr/local/lib
INCDIR	= /usr/local/include
DOCLIB	= /usr/doc

THISLIB	= -L. -ldll
MAJORVERSION = 1
MINORVERSION = 1
PATCHLEVEL = 0

CFLAGS	= $(SHARED) $(OPTIONS) $(OFP) $(DEBUG)
#--------------------------------------------------------------
PROG	= dll_main
TEST	= dll_test
SRCS	= $(PROG).c $(TEST).c
OBJS1	= $(PROG).o
OBJS2	= $(TEST).o
#--------------------------------------------------------------
all	:
	make libdll.so.$(MAJORVERSION).$(MINORVERSION).$(PATCHLEVEL) DEBUG=
	make $(TEST) DEBUG=

debug	:
	make libdll.so.$(MAJORVERSION).$(MINORVERSION).$(PATCHLEVEL) OFP=
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
	$(CC) $(CFLAGS) -c $< 2>$(ERRFILE)

libdll.so.$(MAJORVERSION).$(MINORVERSION).$(PATCHLEVEL): $(OBJS1)
	$(CC) -shared -Wl,-soname,libdll.so.$(MAJORVERSION) \
	 -o libdll.so.$(MAJORVERSION).$(MINORVERSION).$(PATCHLEVEL) $(OBJS1)
	ln -s libdll.so.$(MAJORVERSION).$(MINORVERSION).$(PATCHLEVEL) \
	 libdll.so.$(MAJORVERSION)
	ln -s libdll.so.$(MAJORVERSION) libdll.so

libdll.a: $(OBJS1)
	$(AR) $@ $(OBJS1)

$(TEST)	: $(OBJS2)
	$(CC) $(OBJS2) -o $(TEST) $(THISLIB) 2>{linker}.err

$(PROG).o: $(PROG).c $(PROG).h
$(TEST).o: $(TEST).c linklist.h dll_dbg.h
#--------------------------------------------------------------
html	:
	( cd docs; latex2html -local_icons -no_images Linklist.tex )
	( cd docs/Linklist; rm -rf TMP *.aux *.dvi *.log *.tex *.toc *.pl *.old )
	( cd docs/Linklist; ln -sf ../image.gif img1.gif )

# Be sure to run latex twice or there won't be
# a Table of Contents in the postscript file.
postscript:
	( cd docs; latex Linklist.tex; latex Linklist.tex; \
	 dvips -t letter Linklist.dvi -o Linklist.ps; gzip -9 *.ps )

docs	: postscript html

DISTNAME= linklist-$(MAJORVERSION).$(MINORVERSION).$(PATCHLEVEL)
EXCLUDEFILE= $(DISTNAME)/tar-exclude

# Unless you're me you won't need this.
tarball	:
	( cd ..; tar -czvf $(DISTNAME).tar.gz -X $(EXCLUDEFILE) $(DISTNAME) )

#--------------------------------------------------------------
clean	:
	-rm *.o *~ *.bak \#*\# *.err core

clobber	:
	-rm *.o *~ *.bak \#*\# *.err $(TEST) core libdll.*

distclean: clobber
	( cd docs; rm -rf Linklist *.aux *.dvi *.log *.toc *.ps *.ps.gz )

install	: install-docs
	cp ./libdll.so.$(MAJORVERSION).$(MINORVERSION).$(PATCHLEVEL) $(LIBDIR)
	cp ./linklist.h $(INCDIR)/linklist.h
	cp ./dll_dbg.h $(INCDIR)/dll_dbg.h
	( cd $(LIBDIR); \
	 ln -s libdll.so.$(MAJORVERSION).$(MINORVERSION).$(PATCHLEVEL) \
	 libdll.so.$(MAJORVERSION) )
	( cd $(LIBDIR); ln -s libdll.so.$(MAJORVERSION) libdll.so )
	/sbin/ldconfig

install-static:
	cp ./linklist.h $(INCDIR)/linklist.h
	cp ./dll_dbg.h $(INCDIR)/dll_dbg.h
	cp ./libdll.a $(LIBDIR)/libdll.a

install-docs:
	install -d $(DOCLIB)/$(DISTNAME)
	install -m 444 docs/*.ps.gz $(DOCLIB)/$(DISTNAME)
	install -m 444 docs/Linklist/* $(DOCLIB)/$(DISTNAME)

uninstall: uninstall-docs
	rm -f $(LIBDIR)/libdll.so* $(INCDIR)/linklist.h $(INCDIR)/dll_dbg.h

uninstall-static:
	rm -f $(LIBDIR)/libdll.a $(INCDIR)/linklist.h $(INCDIR)/dll_dbg.h

uninstall-docs:
	rm -rf $(DOCLIB)/$(DISTNAME)
