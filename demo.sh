#!/bin/sh
#
# $Author$
# $Date$
# $Revision$
#
export LD_LIBRARY_PATH=`pwd`:$LD_LIBRARY_PATH
(cd src; ./dll_test)
exit 0
