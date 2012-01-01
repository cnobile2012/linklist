#
# dlinklist/__init__.py
#
# $Author$
# $Date$
# $Revision$
#

__import__("pkg_resources").declare_namespace(__name__)

from dlinklist import SrchOrigin, SrchDir, InsertDir, DLinklist


class BaseLinklistException(Exception):
    __DEFAULT_MESSAGE = "Error: No message given."

    def __init__(self, msg=__DEFAULT_MESSAGE):
        super(BaseLinklistException, self).__init__(msg)
        if not msg: msg = self.__DEFAULT_MESSAGE
        self.__message = str(msg)

    def __str__(self):
        return self.__message


class LibraryNotFoundException(BaseLinklistException):
    __DEFAULT_MESSAGE = "%s not found"

    def __init__(self, msg=""):
        msg = self.__DEFAULT_MESSAGE % msg
        super(LibraryNotFoundException, self).__init__(msg)


class FunctionException(BaseLinklistException):

    def __init__(self, msg):
        super(FunctionException, self).__init__(msg)


class APIException(BaseLinklistException):

    def __init__(self, msg):
        super(APIException, self).__init__(msg)
