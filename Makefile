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

MAJOR_VER	= 2
MINOR_VER	= 0
PATCH_LVL	= 0
DIR_NAME	= linklist-$(MAJOR_VER).$(MINOR_VER).$(PATCH_LVL)

##################################
# CONFIGURE PLATFORM ENVIRONMENT #
##################################
ifeq ($(OS),LINUX)
  prefix  	= /usr/local
  doc_prefix	= /usr/doc
  src_prefix	= $(HOME)/dev/$(DIR_NAME)
  CC            = gcc
  AR            = ar rcs
  MACHINE_OPT   = -m486 -pipe
  COMPILER_OPT  = -ansi -fPIC -Wall -D_REENTRANT -D_GNU_SOURCE -D_DLL_POSIX
  NON_DEBUG_OPT = -O2 -fomit-frame-pointer
  DEBUG_OPT     = -DDEBUG=1 -ggdb -Wundef -Wpointer-arith
  LDFLAGS       += -shared -Wl,-soname,$(BASENAME).so.$(MAJOR_VER)
  TEST_LIBS	= -L. -ldll -lpthread
#  EOBJS		= dll_pthread_ext.o
endif

ifeq ($(OS),SOLARIS)
  prefix  	= $(HOME)/lib
  doc_prefix	= $(HOME)/doc
  src_prefix	= $(HOME)/dev/$(DIR_NAME)
  CC            = /usr/local/SUNWspro/bin/cc
  AR            = ar rcs
  MACHINE_OPT   =
  COMPILER_OPT  = -v -KPIC -mt -xstrconst -D_POSIX_C_SOURCE=199506L \
		  -D_DLL_POSIX
  NON_DEBUG_OPT = -xO5 -dalign -xlibmil
  DEBUG_OPT     = -DDEBUG=1 -g -xF
  LDFLAGS       += -Wl,-G,-h,$(BASENAME).so.$(MAJOR_VER)
  TEST_LIBS	= -L. -ldll -lpthread
  EOBJS		= dll_pthread_ext.o
endif

ifeq ($(OS),OSF1)
  prefix  	= $(HOME)/lib
  doc_prefix	= $(HOME)/doc
  src_prefix	= $(HOME)/$(DIR_NAME)
  CC            = cc
  AR            = ar rcs
  MACHINE_OPT   = -tune ev56
  COMPILER_OPT  = -std1 -warnprotos -D_REENTRANT -pthread -w0 -D_DLL_POSIX
  NON_DEBUG_OPT = -O2 -newc -portable
  DEBUG_OPT     = -DDEBUG=1 -g -trapuv
  LDFLAGS       += -shared -msym -soname $(BASENAME).so.$(MAJOR_VER)
  TEST_LIBS	= -L. -ldll -L/usr/shlib -lpthread
#  EOBJS		= dll_pthread_ext.o
endif

ifeq ($(OS),AIX)
  prefix  	= $(HOME)/lib
  doc_prefix	= $(HOME)/doc
  src_prefix	= $(HOME)/dev/$(DIR_NAME)
  CC            = gcc
  AR            = ar rcs
  MACHINE_OPT   = -pipe
  COMPILER_OPT  = -ansi -Wall
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

ifeq ($(DEBUG),YES)
  CFLAGS        += $(DEBUG_OPT)
else
  CFLAGS        += $(NON_DEBUG_OPT)
endif

# The options below should be used instead of the above on the Mac
#OPTIONS	= -O3 -fstrength-reduce -finline-functions -Wall

LIBDIR		= $(prefix)/lib
INCDIR		= $(prefix)/include
DISTNAME	= linklist-$(MAJOR_VER).$(MINOR_VER).$(PATCH_LVL)-beta
EXCLUDEFILE	= $(DIR_NAME)/tar-exclude

#--------------------------------------------------------------
BASENAME	= libdll
PROG		= dll_main
TEST		= dll_test
SLIB		= $(BASENAME).so.$(MAJOR_VER).$(MINOR_VER).$(PATCH_LVL)
SRCS		= $(PROG).c $(TEST).c
OBJS1		= $(PROG).o $(EOBJS)
OBJS2		= $(TEST).o
#--------------------------------------------------------------
all	:
	make $(SLIB) DEBUG=NO
	make $(TEST)

debug	:
	make $(SLIB) DEBUG=YES
	make $(TEST) DEBUG=YES

static	:
	make $(BASENAME).a DEBUG=NO
	make $(TEST) DEBUG=NO

debug-static :
	make $(BASENAME).a DEBUG=YES
	make $(TEST) DEBUG=YES

# Make the test program from the installed shared libraries.
demo	:
	make $(TEST) DEBUG=NO

.c.o	: $(SRCS)
	$(CC) $(CFLAGS) -c $<

$(SLIB): $(OBJS1)
	$(CC) $(LDFLAGS) $(OBJS1) -o $(SLIB)
	ln -s $(SLIB) $(BASENAME).so.$(MAJOR_VER)
	ln -s $(BASENAME).so.$(MAJOR_VER) $(BASENAME).so

$(BASENAME).a: $(OBJS1)
	$(AR) $@ $(OBJS1)

$(TEST)	: $(OBJS2)
	$(CC) $(OBJS2) -o $(TEST) $(TEST_LIBS)

$(PROG).o: $(PROG).c linklist.h
$(TEST).o: $(TEST).c linklist.h
#--------------------------------------------------------------
html	:
	( cd docs; latex2html -local_icons Linklist.tex )
	( cd docs/Linklist; rm -rf TMP *.aux *.dvi *.log *.tex *.toc *.pl *.old )
	( cd docs/Linklist; ln -sf ../image.gif img1.gif )

# Be sure to run latex twice or there won't be
# a Table of Contents in the postscript file.
postscript:
	( cd docs; latex Linklist.tex; latex Linklist.tex; \
	 dvips -t letter Linklist.dvi -o Linklist.ps; gzip -9 *.ps )

docs	: postscript html

# Unless you're me you won't need this.
tarball	:
	( cd ..; tar -czvf $(DISTNAME).tar.gz -X $(EXCLUDEFILE) $(DIR_NAME) )

#--------------------------------------------------------------
clean	:
	-rm -f *.o *~ *.bak \#*\# core so_locations

clobber	: clean
	-rm $(TEST) $(BASENAME).*

distclean: clobber
	( cd docs; rm -rf Linklist *.aux *.dvi *.log *.toc *.ps *.ps.gz )

install	: install-docs
	cp ./$(SLIB) $(LIBDIR)
	cp ./linklist.h $(INCDIR)/linklist.h
	( cd $(LIBDIR); \
	 ln -s $(SLIB) $(BASENAME).so.$(MAJOR_VER) )
	( cd $(LIBDIR); ln -s $(BASENAME).so.$(MAJOR_VER) $(BASENAME).so )
	/sbin/ldconfig

install-static:
	cp ./linklist.h $(INCDIR)/linklist.h
	cp ./$(BASENAME).a $(LIBDIR)/$(BASENAME).a

install-docs:
	install -d $(DOCLIB)/$(DISTNAME)
	install -m 444 docs/*.ps.gz $(DOCLIB)/$(DISTNAME)
	install -m 444 docs/Linklist/* $(DOCLIB)/$(DISTNAME)

uninstall: uninstall-docs
	-rm -f $(LIBDIR)/$(BASENAME).so* $(INCDIR)/linklist.h

uninstall-static:
	-rm -f $(LIBDIR)/$(BASENAME).a $(INCDIR)/linklist.h

uninstall-docs:
	-rm -rf $(DOCLIB)/$(DISTNAME)
