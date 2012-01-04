#
# dlinklist/__init__.py
#
# $Author$
# $Date$
# $Revision$
#

import pkg_resources as _res

_res.declare_namespace(__name__)
_RES_PATH = _res.resource_filename(__name__, "libdll.so")

from linklist import Return, SrchOrigin, SrchDir, InsertDir, DLinklist


class BaseLinklistException(Exception):
    __DEFAULT_MESSAGE = "Error: No message given."

    def __init__(self, msg=__DEFAULT_MESSAGE):
        super(BaseLinklistException, self).__init__(msg)
        if not msg: msg = self.__DEFAULT_MESSAGE
        self.__message = str(msg)

    def __str__(self):
        return self.__message


class LibraryNotFoundException(BaseLinklistException):

    def __init__(self, msg):
        super(LibraryNotFoundException, self).__init__(msg)


class FunctionException(BaseLinklistException):

    def __init__(self, msg, retval=Return.NORMAL):
        super(FunctionException, self).__init__(msg)
        self._retval = retval

    def getRetval(self):
        return self._retval

class APIException(BaseLinklistException):

    def __init__(self, msg):
        super(APIException, self).__init__(msg)
