#
# Makefile for Doubly Linked List API (Linux version)
#
# Copyright (c) 1996-2011 Carl J. Nobile
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
AR	= ar rcs
CC	= gcc

DEBUG	= -g -DDEBUG
OFP	= -fomit-frame-pointer
SHARED	= -fPIC
OPTIONS	= -O3 -ansi -pipe -fstrength-reduce -finline-functions -Wall \
          -Wno-unused-result

# The options below should be used instead of the above on the Mac
#OPTIONS	= -O3 -fstrength-reduce -finline-functions -Wall

# Change the directory paths below to reflect your system
PREFIX	= /usr/local
LIBDIR	= $(PREFIX)/lib
INCDIR	= $(PREFIX)/include
DOCLIB	= $(PREFIX)/share/doc

# There should be no need to change anything below this line.
THISLIB		= -L. -ldll
MAJORVERSION	= 1
MINORVERSION	= 3
PATCHLEVEL	= 0
VERSION		= ${MAJORVERSION}.${MINORVERSION}.${PATCHLEVEL}
TODAY		= $(shell date +"%Y-%m-%d_%H%M")

CFLAGS	= $(SHARED) $(OPTIONS) $(OFP) $(DEBUG)
#--------------------------------------------------------------
PROG	= dll_main
TEST	= dll_test
SRCS	= $(PROG).c $(TEST).c
OBJS1	= $(PROG).o
OBJS2	= $(TEST).o
#--------------------------------------------------------------
all	: 
	make libdll.so.$(VERSION) DEBUG=
	make $(TEST) DEBUG=

debug	:
	make libdll.so.$(VERSION) OFP=
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

libdll.so.$(VERSION): $(OBJS1)
	$(CC) -shared -Wl,-soname,libdll.so.$(MAJORVERSION) \
         -o libdll.so.$(VERSION) $(OBJS1)
	-ln -sf libdll.so.$(VERSION) libdll.so.$(MAJORVERSION)
	-ln -sf libdll.so.$(MAJORVERSION) libdll.so

libdll.a: $(OBJS1)
	$(AR) $@ $(OBJS1)

$(TEST)	: $(OBJS2)
	$(CC) $(OBJS2) -o $(TEST) $(THISLIB)

$(PROG).o: $(PROG).c linklist.h
$(TEST).o: $(TEST).c linklist.h

runtest	: all
	@(echo; cd test; ./ll_test.py)
#--------------------------------------------------------------
# Be sure to run latex twice or there won't be
# a Table of Contents in the postscript file.
postscript:
	(cd docs; convert linklistDiagram.png -resize 75% linklistDiagram.eps; \
         latex Linklist.tex; latex Linklist.tex; \
	 dvips -t letter Linklist.dvi -o Linklist.ps; gzip -9 *.ps)

pdf	: postscript
	(cd docs; zcat Linklist.ps.gz | ps2pdf - Linklist.pdf)

html	:
	(cd docs; latex2html -local_icons -no_images Linklist.tex)

docs	: html pdf

DISTNAME	= linklist-$(VERSION)
EXCLUDEFILE	= $(DISTNAME)/tar-exclude

# Unless you're me you won't need this.
tarball	: docs log
	(cd ..; tar -czvf $(DISTNAME).tar.gz -X $(EXCLUDEFILE) $(DISTNAME))

cvs-tag	:
	cvs tag ll-${MAJORVERSION}-${MINORVERSION}-${PATCHLEVEL}-${TODAY}

cvs-branch:
	cvs tag -b ll-${MAJORVERSION}-${MINORVERSION}-${PATCHLEVEL}-${TODAY}-br

log	: clean
	@rcs2log -h foundation.TetraSys.org -R > ChangeLog

#--------------------------------------------------------------
clean	:
	@rm -f *.o *~ *.bak \#*\# core test/*~ test/\#*\#

clobber	: clean
	@rm -f libdll.* $(TEST) ChangeLog

distclean: clobber
	@(cd docs; rm -rf Linklist *.aux *.dvi *.log *.toc *.ps *.ps.gz *.eps \
         *.pdf *~ *-pdf.tex)

install	: install-docs
	cp ./libdll.so.$(VERSION) $(LIBDIR)
	cp ./linklist.h $(INCDIR)/linklist.h
	-(cd $(LIBDIR); ln -s libdll.so.$(VERSION) libdll.so.$(MAJORVERSION))
	-(cd $(LIBDIR); ln -s libdll.so.$(MAJORVERSION) libdll.so)
	/sbin/ldconfig

install-static:
	cp ./linklist.h $(INCDIR)/linklist.h
	cp ./libdll.a $(LIBDIR)/libdll.a

install-docs: docs
	install -d $(DOCLIB)/$(DISTNAME)
	install -m 444 docs/*.ps.gz $(DOCLIB)/$(DISTNAME)
	install -m 444 docs/*.pdf $(DOCLIB)/$(DISTNAME)
	install -m 444 docs/Linklist/* $(DOCLIB)/$(DISTNAME)

uninstall: uninstall-docs
	rm -f $(LIBDIR)/libdll.so* $(INCDIR)/linklist.h

uninstall-static:
	rm -f $(LIBDIR)/libdll.a $(INCDIR)/linklist.h

uninstall-docs:
	rm -rf $(DOCLIB)/$(DISTNAME)
