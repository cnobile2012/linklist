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

include linklist.mk

DISTNAME	= linklist-$(VERSION)
EXCLUDEFILE	= $(DISTNAME)/tar-exclude
URL		= http://wiki.tetrasys-design.net

all	: egg
	@(cd src; make all)

debug	:
	@(cd src; make debug)

static	:
	@(cd src; make static)

debug-static :
	@(cd src; make debug-static)

# Make the test program from the installed shared libraries.
test	:
	@(cd src; make test)

runtest	:
	@(cd src; make all)
	@(echo; cd test; ./ll_test.py)

python-api:
	@python setup.py build

egg	: python-api
	@python setup.py bdist_egg

osx-egg	: python-api
	@ARCHFLAGS="-arch i386 -arch x86_64" python setup.py bdist_egg

#env MACOSX_DEPLOYMENT_TARGET=10.6 \
#      SDKROOT=/                     \
#      ARCHFLAGS='-arch x86_64'      \
#      python setup.py build [options]

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

python-docs:
	@(epydoc -v --docformat epytext --name "Doubly Linklist API" \
          -o docs/DLinklist-$(VERSION) --show-private --show-imports \
          --graph all --url "$(URL)" src/dlinklist/*.py test/*.py \
         )

docs	: html pdf python-docs

# Unless you're me you won't need this.
tarball	: docs log
	(cd ..; tar -czvf $(DISTNAME).tar.gz -X $(EXCLUDEFILE) $(DISTNAME); \
         md5sum $(DISTNAME).tar.gz > $(DISTNAME).md5)

cvs-tag	:
	cvs tag ll-${MAJORVERSION}-${MINORVERSION}-${PATCHLEVEL}-${TODAY}

cvs-branch:
	cvs tag -b ll-${MAJORVERSION}-${MINORVERSION}-${PATCHLEVEL}-${TODAY}-br

log	: clean
	@rcs2log -h foundation.TetraSys.org -R > ChangeLog

#--------------------------------------------------------------
clean	:
	@(cd src; make clean)
	@(cd src/dlinklist; rm -f *~ \#*\# *.pyc *.pyo)
	@rm -f *~ \#*\# test/*~ test/\#*\# test/*.pyc test/*.pyo

clobber	: clean
	@(cd src; make clobber)
	@rm -rf ChangeLog build dist

distclean: clobber
	@(cd src; make distclean)
	@(cd docs; rm -rf Linklist DLinklist-$(VERSION) *.aux *.dvi *.log \
         *.toc *.ps *.ps.gz *.eps *.pdf *~ *-pdf.tex)

install	: install-docs
	@(cd src; make install)

install-static:
	@(cd src; make install-static)

install-docs: docs
	install -d $(DOCLIB)/$(DISTNAME)
	install -m 444 docs/*.ps.gz $(DOCLIB)/$(DISTNAME)
	install -m 444 docs/*.pdf $(DOCLIB)/$(DISTNAME)
	install -m 444 docs/Linklist/* $(DOCLIB)/$(DISTNAME)

uninstall: uninstall-docs
	rm -f $(LIBDIR)/libdll.so* $(INCDIR)/linklist.h

uninstall-static:
	@(cd src; make uninstall-static)

uninstall-docs:
	rm -rf $(DOCLIB)/$(DISTNAME)
