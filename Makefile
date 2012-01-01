#
# Makefile for Doubly Linked List API
#
# Copyright (c) 1996-2000 Carl J. Nobile
# Created: May 26, 1997
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

include osdetect.mk

PACKAGE_PREFIX  = $(shell pwd)
MAJOR_VER	= 2
MINOR_VER	= 0
PATCH_LVL	= 0
VERSION		= $(MAJOR_VER).$(MINOR_VER).$(PATCH_LVL)
DIR_NAME	= linklist-$(VERSION)
DISTNAME	= $(DIR_NAME)-beta # Remove -beta when not a beta anymore.

##################################
# CONFIGURE PLATFORM ENVIRONMENT #
##################################
ifeq ($(OS),LINUX)
  prefix  	= /usr/local
  doc_prefix	= /usr/doc
  src_prefix	= $(PACKAGE_PREFIX)
  CC            = gcc
  AR            = ar rcs
  MACHINE_OPT   = -pipe
  COMPILER_OPT  = -ansi -fPIC -Wall -D_REENTRANT -D_GNU_SOURCE -D_DLL_PTHREADS \
                  -Wno-unused-result
  NON_DEBUG_OPT = -O2 -fomit-frame-pointer
  DEBUG_OPT     = -DDEBUG=1 -ggdb -Wundef -Wpointer-arith
  LDFLAGS       += -shared -Wl,-soname,$(BASENAME).so.$(MAJOR_VER)
  TEST_LIBS	= -L. -ldll -lpthread
#  EOBJS		= dll_pthread_ext.o
endif

ifeq ($(OS),SOLARIS)
  prefix  	= /usr/local
  doc_prefix	= /usr/doc
  src_prefix	= $(PACKAGE_PREFIX)
  CC            = /usr/local/SUNWspro/bin/cc
  AR            = ar rcs
  MACHINE_OPT   =
  COMPILER_OPT  = -v -KPIC -mt -xstrconst -D_POSIX_C_SOURCE=199506L \
		  -D_DLL_PTHREADS
  NON_DEBUG_OPT = -xO5 -dalign -xlibmil
  DEBUG_OPT     = -DDEBUG=1 -g -xF
  LDFLAGS       += -Wl,-G,-h,$(BASENAME).so.$(MAJOR_VER)
  TEST_LIBS	= -L. -ldll -lpthread
  EOBJS		= dll_pthread_ext.o
endif

ifeq ($(OS),OSF1)
  prefix  	= /usr/local
  doc_prefix	= /usr/doc
  src_prefix	= $(PACKAGE_PREFIX)
  CC            = cc
  AR            = ar rcs
  MACHINE_OPT   = -tune ev56
  COMPILER_OPT  = -std1 -warnprotos -D_REENTRANT -pthread -w0 -D_DLL_PTHREADS
  NON_DEBUG_OPT = -O2 -newc -portable
  DEBUG_OPT     = -DDEBUG=1 -g -trapuv
  LDFLAGS       += -shared -msym -soname $(BASENAME).so.$(MAJOR_VER)
  TEST_LIBS	= -L. -ldll -L/usr/shlib -lpthread
#  EOBJS		= dll_pthread_ext.o
endif

ifeq ($(OS),AIX)
  prefix  	= /usr/local
  doc_prefix	= /usr/doc
  src_prefix	= $(PACKAGE_PREFIX)
  CC            = gcc
  AR            = ar rcs
  MACHINE_OPT   = -pipe
  COMPILER_OPT  = -ansi -Wall -Wno-unused-result
  NON_DEBUG_OPT = -O2 -fomit-frame-pointer
  DEBUG_OPT     = -DDEBUG=1 -ggdb -Wundef -Wpointer-arith
  LDFLAGS       += -Wl,-G,-bshared
  TEST_LIBS	= -L. -ldll -lpthread
#  EOBJS		= dll_pthread_ext.o
endif

#----- Change Nothing Below This Line -------------------------

###################
# ASSEMBLE CFLAGS #
###################
CFLAGS          += -D$(OS) $(MACHINE_OPT) $(COMPILER_OPT)

# Set DEBUG flag
ifeq ($(DEBUG),YES)
  CFLAGS        += $(DEBUG_OPT)
else
  CFLAGS        += $(NON_DEBUG_OPT)
endif

# Set THREAD flag
ifeq ($(THREAD),YES)
  CFLAGS        += -D_DLL_THREADS
  EOBJS		+= dll_lock_wrappers.o
endif

# The options below should be used instead of the above on the Mac
LIBDIR		= $(prefix)/lib
INCDIR		= $(prefix)/include
EXCLUDEFILE	= $(DIR_NAME)/tar-exclude

#--------------------------------------------------------------
BASENAME	= libdll
PROG		= dll_main
TEST		= dll_test
SLIB		= $(BASENAME).so.$(VERSION)
SRCS		= $(PROG).c $(TEST).c
OBJS1		= $(PROG).o $(EOBJS) 
OBJS2		= $(TEST).o
#--------------------------------------------------------------
all	:
	make $(SLIB) THREAD=YES DEBUG=NO 
	make $(TEST) THREAD=YES DEBUG=NO

no-threads :
	make $(SLIB) THREAD=NO DEBUG=NO 
	make $(TEST) THREAD=NO DEBUG=NO

debug	:
	make $(SLIB) THREAD=YES DEBUG=YES
	make $(TEST) THREAD=YES DEBUG=YES

static	:
	make $(BASENAME).a THREAD=YES DEBUG=NO
	make $(TEST) THREAD=YES DEBUG=NO

debug-static :
	make $(BASENAME).a THREAD=YES DEBUG=YES
	make $(TEST) THREAD=YES DEBUG=YES

# Make the test program from the installed shared libraries.
demo	:
	make $(TEST) THREAD=YES DEBUG=NO

.c.o	: $(SRCS)
	$(CC) $(CFLAGS) -c $<

$(SLIB): $(OBJS1)
	$(CC) $(LDFLAGS) $(OBJS1) -o $(SLIB)
	-ln -sf $(SLIB) $(BASENAME).so.$(MAJOR_VER)
	-ln -sf $(BASENAME).so.$(MAJOR_VER) $(BASENAME).so

$(BASENAME).a: $(OBJS1)
	$(AR) $@ $(OBJS1)

$(TEST)	: $(OBJS2)
	$(CC) $(OBJS2) -o $(TEST) $(TEST_LIBS)

$(PROG).o: $(PROG).c linklist.h
$(TEST).o: $(TEST).c linklist.h
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

EXCLUDEFILE= $(DIR_NAME)/tar-exclude

# Unless you're me you won't need this.
tarball	: docs log clobber
	(cd ..; tar -czvf $(DISTNAME).tar.gz -X $(EXCLUDEFILE) $(DIR_NAME))

log	: clean
	@rcs2log -h foundation.TetraSys.org -R > ChangeLog
#--------------------------------------------------------------
clean	:
	@rm -f *.o *~ *.bak \#*\# core

clobber	: clean
	@rm $(TEST) $(BASENAME).*
	@(cd docs; rm -rf *.aux *.log *.toc *.eps *~ *-pdf.tex)

distclean: clobber
	@rm -f ChangeLog
	@(cd docs; rm -rf Linklist *.dvi *.ps *.ps.gz *.pdf)

install	: install-docs
	cp ./$(SLIB) $(LIBDIR)
	cp ./linklist.h $(INCDIR)/linklist.h
	-(cd $(LIBDIR); ln -s $(SLIB) $(BASENAME).so.$(MAJOR_VER))
	-(cd $(LIBDIR); ln -s $(BASENAME).so.$(MAJOR_VER) $(BASENAME).so)
	/sbin/ldconfig

install-static:
	cp ./linklist.h $(INCDIR)/linklist.h
	cp ./$(BASENAME).a $(LIBDIR)/$(BASENAME).a

install-docs: docs
	install -d $(DOCLIB)/$(DISTNAME)
	install -m 444 docs/*.ps.gz $(DOCLIB)/$(DISTNAME)
	install -m 444 docs/*.pdf $(DOCLIB)/$(DISTNAME)
	install -m 444 docs/Linklist/* $(DOCLIB)/$(DISTNAME)

uninstall: uninstall-docs
	-rm -f $(LIBDIR)/$(BASENAME).so* $(INCDIR)/linklist.h

uninstall-static:
	-rm -f $(LIBDIR)/$(BASENAME).a $(INCDIR)/linklist.h

uninstall-docs:
	-rm -rf $(DOCLIB)/$(DISTNAME)
