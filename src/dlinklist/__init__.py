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

from linklist import Return, SrchOrigin, SrchDir, InsertDir, Info, DLinklist


class BaseLinklistException(Exception):
    """
    The base exception for all Dlinklist exceptions.
    """
    __DEFAULT_MESSAGE = "Error: No message given."

    def __init__(self, msg=__DEFAULT_MESSAGE):
        """
        Call the standard Python Exception constructor and sets the default
        message if no message provided.

        @keyword msg: The message to return when raised.
        @type msg: C{str}
        """
        super(BaseLinklistException, self).__init__(msg)
        if not msg: msg = self.__DEFAULT_MESSAGE
        self.__message = str(msg)

    def __str__(self):
        return self.__message


class LibraryNotFoundException(BaseLinklistException):
    """
    Raised if the C{C} link list library is not found.
    """

    def __init__(self, msg):
        """
        Call the C{BaseLinklistException} constructor.

        @param msg: The message to return when raised.
        @type msg: C{str}
        """
        super(LibraryNotFoundException, self).__init__(msg)


class FunctionException(BaseLinklistException):
    """
    Raised if the C{Return.NORMAL} value is not returned by a C{C} function.
    """

    def __init__(self, msg, retval=Return.NORMAL):
        """
        Call the C{BaseLinklistException} constructor and sets the C{Return}
        value. The default is C{Return.NORMAL} if no return value is provided.

        @param msg: The message to return when raised.
        @type msg: C{str}
        @keyword retval: One of the enumerated objects from the C{Return} class.
        @type retval: C{int}
        """
        super(FunctionException, self).__init__(msg)
        self._retval = retval

    def getRetval(self):
        """
        Get the C{Return} value.

        @return: An enumerated object from the C{Return} class.
        @rtype: C{int}
        """
        return self._retval

class APIException(BaseLinklistException):
    """
    Raised if the low level C{C} functions encounter an error.
    """

    def __init__(self, msg):
        """
        Call the C{BaseLinklistException} constructor.

        @param msg: The message to return when raised.
        @type msg: C{str}
        """
        super(APIException, self).__init__(msg)
