#
# dlinklist/__init__.py
#
# $Author$
# $Date$
# $Revision$
#

"""
B{Overview}

The Python API is a I{ctypes} representation of the C API. It has slightly
different functionality that the C API, however its usage is very similar.

Instead of function in a module it has been implimented as a class therefore
taking advantage of private and protected objects to give a cleaner interface.

B{Installation}

It is simple to install the Python egg::

  $ sudo easy_install linklist-2.0.0.tar.gz

  or

  $ cd linklist-2.0.0
  $ make egg
  $ sudo easy_install dist/DLinklist*.egg

B{Usage}

The first thing that needs to be done is to create your C{Info} class. There
are two ways to do this.

  1. Use the class that is already created::
    from dlinklist import Info

    Info._fields_.append(('field01', c_char * 100))
    Info._fields_.append(('field02', c_char * 100))

  2. Make a new class::
    from ctypes import Structure

    class Info(Structure):
        _fields_ = (
            ('field01', c_char * 100),
            ('field02', c_char * 100),
            )

Note: If you need to make a reference to the C{Info} class itself it will
need to be done as in number 1 above, even if you create your own class.

The next thing that needs to be done is to create the C{List} object. We
actually will not be creating a C{List} object as we did with the C{Info} class,
this will be done within the library itself.

Instantiate the C{DLinklist} class and create the C{List} object::
  from dlinklist import *
  from ctypes import sizeof

  dll = DLinklist()
  dll.create(sizeof(Info))

And you are done, just call any method in the C{DLinklist} class on the
C{dll} object.

@note: All the C{pFun} objects in the API need to return C{< 0}, C{0}, and
       C{> 0} as in the Python I{cmp} function. The C{compare} method in the
       API is very basic, so you will probably need to write your own. However,
       use the C{compare} method in the source code as an example of how it
       should be written.
"""

__all__ = ('linklist',)

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
