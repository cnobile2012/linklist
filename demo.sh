#!/bin/sh
#
# $Author$
# $Date$
# $Revision$
#
CWD=`pwd`
LD_LIBRARY_PATH=$CWD:$LD_LIBRARY_PATH
export LD_LIBRARY_PATH
$CWD/dll_test
