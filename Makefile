#
# Makefile for Doubly Linked List API (Linux version)
#
# Carl J. Nobile
# Created: May 26, 1997
# Updated: 06/08/98
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

LIBDIR	= /usr/local/lib
INCDIR	= /usr/local/include
THISLIB	= -L.
LIBS	= -ldll -lm
MJV	= 1
MNV	= 0.2

CFLAGS	= $(SHARED) $(OPTIONS) $(OFP) $(DEBUG)
#--------------------------------------------------------------
PROG	= dll_main
TEST	= dll_test
SRCS	= $(PROG).c $(TEST).c
OBJS1	= $(PROG).o
OBJS2	= $(TEST).o
#--------------------------------------------------------------
all	:
	make libdll.so.$(MJV).$(MNV) DEBUG=
	make $(TEST) DEBUG=

static	:
	make libdll.a SHARED= DEBUG=
	make $(TEST) SHARED= DEBUG=

debug	:
	make libdll.so.$(MJV).$(MNV) OFP=
	make $(TEST) OFP=

debug-static :
	make libdll.a SHARED= OFP=
	make $(TEST) SHARED= OFP=

test	:
	make $(TEST) DEBUG= THISLIB=

.c.o	: $(SRCS)
	$(CC) $(CFLAGS) -c $< 2>$(ERRFILE)

libdll.so.$(MJV).$(MNV): $(OBJS1)
	$(CC) -shared -Wl,-soname,libdll.so.$(MJV) -o libdll.so.$(MJV).$(MNV) \
	 $(OBJS1)
	ln -s libdll.so.$(MJV).$(MNV) libdll.so.$(MJV)
	ln -s libdll.so.$(MJV) libdll.so
	( export LD_LIBRARY_PATH=`pwd`:$LD_LIBRARY_PATH )

libdll.a: $(OBJS1)
	$(AR) $@ $(OBJS1)

$(TEST)	: $(OBJS2)
	$(CC) $(OBJS2) -o $(TEST) $(THISLIB) $(LIBS) 2>{linker}.err

$(PROG).o: $(PROG).c $(PROG).h
$(TEST).o: $(TEST).c linklist.h
#--------------------------------------------------------------
clean	:
	-rm *.o *~ *.bak \#*\# *.err core

clobber	:
	-rm *.o *~ *.bak \#*\# *.err $(TEST) core libdll.*

install	:
	rm -f $(LIBDIR)/libdll.so*
	cp ./libdll.so.$(MJV).$(MNV) $(LIBDIR)/libdll.so.$(MJV).$(MNV)
	cp ./linklist.h $(INCDIR)/linklist.h
	/sbin/ldconfig
	( cd $(LIBDIR); ln -s libdll.so.$(MJV) libdll.so )

install-static:
	cp ./libdll.a $(LIBDIR)/libdll.a
	cp ./linklist.h $(INCDIR)/linklist.h
