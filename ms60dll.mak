#
# Makefile for LLIBDLL.lib  (MS C Version 6.0)
#
# Copyright (c) 1996-1998 Carl J. Nobile
# Created: January 10, 1997
# Updated: 11/04/98
#
# $Author$
# $Date$
# $Revision$
#
CC	= cl
LD	= link
RM	= rm
AR	= lib
C6PATH	= c:
MYNAME	= mslibdll.mak

MODEL	= L
LIB	= .\;$(C6PATH)\c600\lib
ERRFILE	= {$*}.err
DEBUG	= -DDEBUG -Od -Zi
OPTIONS	= -Ox -W4 -A$(MODEL)
CFLAGS	= $(OPTIONS) $(DEBUG) /F A000

#-------------------------------------------------
PROG	= dll_main
TEST	= dll_test
SRCS	= $(PROG).c $(TEST).c
OBJS1	= $(PROG).obj
OBJS2	= $(TEST).obj

#-------------------------------------------------
.SUFFIXES : .obj

all	: 
	make -f$(MYNAME) $(MODEL)libdll.lib DEBUG=
	make -f$(MYNAME) $(TEST).exe DEBUG=

debug	: 
	make -f$(MYNAME) $(MODEL)libdll.lib OPTIONS=
	make -f$(MYNAME) $(TEST).exe OPTIONS=

.c.obj	:
	$(CC) $(CFLAGS) -c $< >$(ERRFILE)

$(MODEL)libdll.lib: $(OBJS1)
	$(RM) $@
	$(AR) $@ +$(OBJS1);

$(TEST).exe: $(OBJS2)
	$(CC) $(OBJS2) $(CFLAGS) $(MODEL)libdll.lib >{link}.err

$(PROG).obj: $(PROG).c $(PROG).h
$(TEST).obj: $(TEST).c linklist.h $(MODEL)libdll.lib

#-------------------------------------------------
clean	:
	$(RM) *.obj *.err

clobber	:
	$(RM) *.obj *.err *.exe $(MODEL)libdll.lib

rmlib	:
	$(RM) $(MODEL)libdll.lib

install	:
	copy $(MODEL)libdll.lib $(C6PATH)\c600\lib\$(MODEL)libdll.lib
	copy linklist.h $(C6PATH)\c600\include\linklist.h
