#
# dlinklist/linklist.py
#
# ctypes wrappers for the Doubly Linked list API.
#
# $Author$
# $Date$
# $Revision$
#

import logging, os
from ctypes import CDLL, CFUNCTYPE, POINTER, Structure, byref, cast, \
     string_at, c_void_p, c_int, c_ulong, c_bool, c_size_t, c_char_p


import dlinklist as dll


class Return(object):
    """
    Many methods in the API return a status value, this class provides an
    enumeration of the status valid return values.
    """
    NORMAL = 0        # normal operation
    MEM_ERROR = 1     # malloc error
    ZERO_INFO = 2     # sizeof(Info) is zero
    NULL_LIST = 3     # List is NULL
    NOT_FOUND = 4     # Record not found
    OPEN_ERROR = 5    # Cannot open file
    WRITE_ERROR = 6   # File write error
    READ_ERROR = 7    # File read error
    NOT_MODIFIED = 8  # Unmodified list
    NULL_FUNCTION = 9 # NULL function pointer
    CONTINUE = 10     # Continue process--internal use only
    _ERRORS = None
    __MESSAGES = {
        0: "Normal operation",
        1: "malloc error",
        2: "sizeof(Info) is zero",
        3: "List is NULL",
        4: "Record not found",
        5: "Cannot open file",
        6: "File write error",
        7: "File read error",
        8: "Unmodified list",
        9: "NULL function pointer",
        10: "Continue process--internal use only",
        }

    @classmethod
    def getMessage(self, num):
        """
        Return a tuple consisting of the text name of the status return value
        and the description of the status. If the return value is invalid the
        number of the value is returned and the phrase 'Unknown error'.

        @param num: The numeric value from the C{Return} class.
        @type num: C{int}
        @return: A tuple consisting of the text C{Return} value and the
                 description.
        @rtype: C{(str} or C{int, str)}
        """
        return (self._ERRORS.get(num, num),
                self.__MESSAGES.get(num, "Unknown error"))

Return._ERRORS = dict([(v,k) for k,v in Return.__dict__.items()
                       if not k.startswith("_")])


class SrchOrigin(object):
    """
    Provides an enumeration of the search origin values.
    """
    ORIGIN_DEFAULT = 0 # Use current origin setting
    HEAD = 1           # Set origin to head pointer
    CURRENT = 2        # Set origin to current pointer
    TAIL = 3           # Set origin to tail pointer
    _ORIGINS = None
    __MESSAGES = {
        0: "Use current origin setting",
        1: "Set origin to head pointer",
        2: "Set origin to current pointer",
        3: "Set origin to tail pointer",
        }

    @classmethod
    def getMessage(self, num):
        """
        Return a tuple consisting of the text name of the search origin value
        and the description of the status. If the search origin value is
        invalid the number of the value is returned and the phrase
        'Unknown error'.

        @param num: The numeric value from the C{SrchOrigin} class.
        @type num: C{int}
        @return: A tuple consisting of the text C{SrchOrigin} value and the
                 description.
        @rtype: C{(str} or C{int, str)}
        """
        return (self._ORIGINS.get(num, num),
                self.__MESSAGES.get(num, "Unknown search origin"))

SrchOrigin._ORIGINS = dict([(v,k) for k,v in SrchOrigin.__dict__.items()
                            if not k.startswith("_")])


class SrchDir(object):
    """
    Provides an enumeration of the search direction values.
    """
    DIRECTION_DEFAULT = 0 # Use current direction setting
    DOWN = 1              # Set direction to down
    UP = 2                # Set direction to up
    _DIRS = None
    __MESSAGES = {
        0: "Use current direction setting",
        1: "Set direction to down",
        2: "Set direction to up",
        }

    @classmethod
    def getMessage(self, num):
        """
        Return a tuple consisting of the text name of the search direction value
        and the description of the status. If the search direction value is
        invalid the number of the value is returned and the phrase
        'Unknown error'.

        @param num: The numeric value from the C{SrchDir} class.
        @type num: C{int}
        @return: A tuple consisting of the text C{SrchDir} value and the
                 description.
        @rtype: C{(str} or C{int, str)}
        """
        return (self._DIRS.get(num, num),
                self.__MESSAGES.get(num, "Unknown search direction"))

SrchDir._DIRS = dict([(v,k) for k,v in SrchDir.__dict__.items()
                      if not k.startswith("_")])


class InsertDir(object):
    """
    Provides an enumeration of the insert direction values.
    """
    INSERT_DEFAULT = 0 # Use current insert setting
    ABOVE = 1          # Insert new record ABOVE current record
    BELOW = 2          # Insert new record BELOW current record
    _DIRS = None
    __MESSAGES = {
        0: "Use current insert setting",
        1: "Insert new record ABOVE current record",
        2: "Insert new record BELOW current record",
        }

    @classmethod
    def getMessage(self, num):
        """
        Return a tuple consisting of the text name of the insert direction value
        and the description of the status. If the insert direction value is
        invalid the number of the value is returned and the phrase
        'Unknown error'.

        @param num: The numeric value from the C{InsertDir} class.
        @type num: C{int}
        @return: A tuple consisting of the text C{InsertDir} value and the
                 description.
        @rtype: C{(str} or C{int, str)}
        """
        return (self._DIRS.get(num, num),
                self.__MESSAGES.get(num, "Unknown search direction"))

InsertDir._DIRS = dict([(v,k) for k,v in InsertDir.__dict__.items()
                        if not k.startswith("_")])


class Node(Structure):
    """
    This class holds the link list pointers and the Info structure pointer.
    """
    _fields_ = [
        ('info', c_void_p),
        ]
Node._fields_.append([('next', POINTER(Node)),
                      ('prior', POINTER(Node))])


class List(Structure):
    """
    This is the top level control structure which keeps track of the Node
    structure pointers and various variables used in the API.
    """
    _fields_ = (
        ('head', POINTER(Node)),
        ('tail', POINTER(Node)),
        ('current', POINTER(Node)),
        ('saved', POINTER(Node)),
        ('infosize', c_int),
        ('listsize', c_ulong),
        ('current_index', c_ulong),
        ('save_index', c_ulong),
        ('modified', c_bool),
        ('search_origin', c_int),
        ('search_dir', c_int),
        )


class SearchModes(Structure):
    """
    This class is returned by the getSearchModes() method and contains the
    current search origin and direction modes from the Controller List class.
    """
    _fields_ = (
        ('search_origin', c_int),
        ('search_dir', c_int),
        )


class DLinklist(object):
    """
    This class provides thin wrappers around the functions in my doubly linklist
    C library.

      1. Initialization Methods
        - C{create()} -- Creates and initializes the link list. This method
          both creates and initializes the list and should be used in
          preference to the next two methods except in rare cases.
        - C{createList()} -- List creation method.
        - C{initialize()} -- List initialization method.
        - C{destroyList()} -- List removal method.

      2. Status and State Methods
        - C{version()} -- Get the version information and a list of
          contributers to this project.
        - C{isListEmpty()} -- Check if the list is empty.
        - C{isListFull()} -- Check if the list is full.
        - C{getNumberOfRecords()} -- Get the number of records in the link
          list.
        - C{setSearchModes()} -- Sets the search C{origin} and C{dir} modes.
        - C{getSearchModes()} -- Get the search modes, returns a tuple of
          origin and direction.
        - C{getCurrentIndex()} -- Get the current index value.

      3. Pointer Manipulation Methods
        - C{currentPointerToHead()} -- Moves the current pointer to the head
          of the list.
        - C{currentPointerToTail()} -- Moves the current pointer to the tail
          of the list.
        - C{incrementCurrentPointer()} -- Moves the current pointer to the
          next C{Node}.
        - C{decrementCurrentPointer()} -- Moves the current pointer to the
          prior C{Node}.
        - C{storeCurrentPointer()} -- Store the current pointer in the control
          C{List} class.
        - C{restoreCurrentPointer()} -- Restore the current pointer from the
          control C{List} class.

      4. List Update Methods
        - C{addRecord()} -- Adds a record to the link list.
        - C{insertRecord()} -- Inserts a record relative to the current
          pointer.
        - C{swapRecord()} -- Swaps current record up or down one place in the
          list.
        - C{updateCurrentRecord()} -- Updates the current record.
        - C{deleteCurrentRecord()} -- Delete a record from the list.
        - C{deleteAllNodes()} -- Deletes all the C{Info} and their C{Node}
          objects from the list then reinitializes the control C{List}.

      5. Search and Retrieval Methods
        - C{findRecord()} -- Find a C{record} in the list with search criteria
          passed into C{match}.
        - C{findNthRecord()} -- Returns the Nth record in the list based on
          the setting of origin and direction values in the control C{List}.
        - C{getCurrentRecord()} -- Get the current record.
        - C{getPriorRecord()} -- Get the prior record relative to the current
          pointer.
        - C{getNextRecord()} -- Get the next record relative to the current
          pointer.

      6. Input/Output Methods
        - C{saveList()} -- Save list to disk.
        - C{loadList()} -- Load list to disk.

      7. Miscellaneous Helper Methods
        - C{compare()} -- A basic compare function. You may need to write
          your own.
    """
    __LIBRARY = ("../src/libdll.so", dll._RES_PATH, "../libdll.so",)

    def __init__(self, logname="", disableLogging=False):
        """
        The constructor creates logging and instantiates the library object.

        @keyword logname: The logging name used in your application, defaults
                          to the root logger.
        @type logname: C{str}
        @keyword disableLogging: Turns logging on or off. The default C{False}
                                 turns logging on, and C{True} turns logging
                                 off.
        @type disableLogging: C{bool}
        @raise LibraryNotFoundException: If the C{C} library cannot be found.
        """
        if not logname: logging.basicConfig()
        self._log = logging.getLogger(logname)
        self._log.setLevel(logging.DEBUG)
        if disableLogging: logging.disable(100)
        self._lib = None

        for path in self.__LIBRARY:
            try:
                self._lib = CDLL(path)
                break
            except:
                pass

        if not self._lib:
            lib = os.path.split(self.__LIBRARY[0])[1]
            msg = "Could not load library: %s"
            self._log.critical(msg, lib)
            raise dll.LibraryNotFoundException(msg % lib)

        self._list_p = None

    #
    # Initialization Methods
    #

    def create(self, infoSize):
        """
        Creates and initializes the link list. This method should be used
        instead of the C{createList} and C{initialize} methods unless you need
        to reuse the C{List} class.

        @param infoSize: The size of the user defined C{Info} class.
        @type infoSize: C{int}
        @return: The C{ctypes} C{POINTER} object that points to the top level
                 C{List} class.
        @rtype: C{ctypes} C{POINTER}
        @raise APIException: If a low level error occurred in the C{C} code.
        @raise FunctionException: If the status return value is not
                                  C{Return.NORMAL}.
        """
        list_p = self.createList()
        self.initialize(infoSize)
        return list_p

    def createList(self):
        """
        Creates the C{List} object in memory.

        The C{C} function doc string::

          List *DLL_CreateList(List **list);

          Arguments: list -- Pointer to a pointer to a name of a structure to
                             create.
          Returns  : Pointer to created structure NULL if unsuccessful}

        @return: A pointer to the top level C{List} class.
        @rtype: C{ctypes} C{POINTER}
        @raise APIException: If a low level error occurred in the C{C} code.
        """
        try:
            createList = self._lib.DLL_CreateList
            createList.argtypes = (POINTER(POINTER(List)),)
            createList.restype = POINTER(List)
            control = POINTER(List)()
            list_p = createList(byref(control))
        except Exception, e:
            self._log.critical("Unknown error: %s", str(e))
            raise dll.APIException(e)

        self._log.debug("List address: %s", hex(cast(list_p, c_void_p).value))
        self._list_p = list_p
        return list_p

    def initialize(self, infoSize):
        """
        Initializes the C{List} class with the user's C{Info} class size
        parameters.

        The C{C} function doc string::

          DLL_Return DLL_InitializeList(List *list, size_t infosize);

          Arguments: list          -- Pointer to type List
                     infosize      -- Size of user Info
          Returns  : DLL_NORMAL    -- Initialization was done successfully
                     DLL_ZERO_INFO -- sizeof(Info) is zero
                     DLL_NULL_LIST -- Info is NULL

        @param infoSize: The size of the user defined C{Info} class.
        @type infoSize: C{int}
        @return: C{None}
        @raise APIException: If a low level error occurred in the C{C} code.
        @raise FunctionException: If the status return value is not
                                  C{Return.NORMAL}.
        """
        try:
            initList = self._lib.DLL_InitializeList
            initList.argtypes = (POINTER(List), c_size_t)
            retval = initList(self._list_p, c_size_t(infoSize))
        except Exception, e:
            self._log.critical("Unknown error: %s", str(e))
            raise dll.APIException(e)

        if retval != Return.NORMAL:
            msg = "Return.%s: %s" % Return.getMessage(retval)
            raise dll.FunctionException(msg, retval=retval)

    def destroyList(self):
        """
        Deallocates the memory of all C{Nodes} and the C{Info} objects then
        deallocates the memory used by the C{List} object.

        The C{C} function doc string::

          void DLL_DestroyList(List **list);

          Arguments: list -- Pointer to a pointer to a name of a structure to
                             destroy.
          Returns  : void

        @return: C{None}
        @raise APIException: If a low level error occurred in the C{C} code.
        """
        try:
            destroyList = self._lib.DLL_DestroyList
            destroyList.argtypes = (POINTER(POINTER(List)),)
            destroyList.restype = None
            destroyList(byref(self._list_p))
        except Exception, e:
            self._log.critical("Unknown error: %s", str(e))
            raise dll.APIException(e)

    #
    # Status and State Methods
    #

    def version(self):
        """
        Get the version information and a list of contributors to this project.

        The C{C} function doc string::

          DLL_Version() : Returns a pointer to version information

          Arguments: void

          Return   : char * -- Pointer to version info

        @return: A printable string.
        @rtype: C{str}
        @raise APIException: If a low level error occurred in the C{C} code.
        """
        try:
            version = string_at(self._lib.DLL_Version())
        except Exception, e:
            self._log.critical("Unknown error: %s", str(e))
            raise dll.APIException(e)

        return version

    def isListEmpty(self):
        """
        Check if the list is empty.

        The C{C} function doc string::

          DLL_Boolean DLL_IsListEmpty(List *list);

          Arguments: list      -- Pointer to type List
          Returns  : DLL_TRUE  -- List is empty
                     DLL_FALSE -- List has items in it

        @return: If the list is empty return C{True} else return C{False}.
        @rtype: C{bool}
        @raise APIException: If a low level error occurred in the C{C} code.
        """
        try:
            isListEmpty = self._lib.DLL_IsListEmpty
            isListEmpty.argtypes = (POINTER(List),)
            retval = isListEmpty(self._list_p)
        except Exception, e:
            self._log.critical("Unknown error: %s", str(e))
            raise dll.APIException(e)

        return retval

    def isListFull(self):
        """
        Check if the list is full, meaning memory is exhausted.

        The C{C} function doc string::

          DLL_Boolean DLL_IsListFull(List *list);

          Arguments: list      -- Pointer to type List
          Returns  : DLL_TRUE  -- List is full (memory dependent)
                     DLL_FALSE -- List is empty or partially full

        @return: If the list is full return C{True} else return C{False}.
        @rtype: C{bool}
        @raise APIException: If a low level error occurred in the C{C} code.
        """
        try:
            isListFull = self._lib.DLL_IsListFull
            isListFull.argtypes = (POINTER(List),)
            retval = isListFull(self._list_p)
        except Exception, e:
            self._log.critical("Unknown error: %s", str(e))
            raise dll.APIException(e)

        return retval

    def getNumberOfRecords(self):
        """
        Get the number of records in the link list.

        The C{C} function doc string::

          unsigned long DLL_GetNumberOfRecords(List *list);

          Arguments: list -- Pointer to type List
          Returns  : Number of records in list

        @return: The number of records in the link list.
        @rtype: C{int}
        @raise APIException: If a low level error occurred in the C{C} code.
        """
        try:
            getNumberOfRecords = self._lib.DLL_GetNumberOfRecords
            getNumberOfRecords.argtypes = (POINTER(List),)
            retval = getNumberOfRecords(self._list_p)
        except Exception, e:
            self._log.critical("Unknown error: %s", str(e))
            raise dll.APIException(e)

        return retval

    def setSearchModes(self, origin, dir):
        """
        Sets the search C{origin} and C{dir} modes.

        The C{C} function doc string::

          DLL_Return DLL_SetSearchModes(List *list, DLL_SrchOrigin origin,
                                        DLL_SrchDir dir);

          Arguments: list             -- Pointer to type List
                     origin           -- Indicates the start search pointer to
                                         use
                     dir              -- Indicates the direction to search in
          Returns  : DLL_NORMAL       -- Values assigned were accepted
                     DLL_NOT_MODIFIED -- Values were not assigned--invalid type
                                         (previous values are still in place)

        @param origin: A value from the C{SrchOrigin} class.
        @type origin: C{int}
        @param dir: A value from  the C{SrchDir} class.
        @type dir: C{int}
        @return: C{None}
        @raise APIException: If a low level error occurred in the C{C} code.
        @raise FunctionException: If the status return value is not
                                  C{Return.NORMAL}.
        """
        try:
            setSearchModes = self._lib.DLL_SetSearchModes
            setSearchModes.argtypes = (POINTER(List), c_int, c_int)
            retval = setSearchModes(self._list_p, origin, dir)
        except Exception, e:
            self._log.critical("Unknown error: %s", str(e))
            raise dll.APIException(e)

        if retval != Return.NORMAL:
            msg = "Return.%s: %s" % Return.getMessage(retval)
            raise dll.FunctionException(msg, retval=retval)

    def getSearchModes(self):
        """
        Get the search modes, returns a tuple of origin and direction.

        The C{C} function doc string::

          DLL_SearchModes DLL_GetSearchModes(List *list, DLL_SearchModes *ssp);

          Arguments: list -- Pointer to type List
                     ssp  -- Save structure pointer
          Returns  : Pointer to type DLL_SearchModes

        @return: The search modes in a tuple C{(origin, direction)}.
        @rtype: C{tuple}
        @raise APIException: If a low level error occurred in the C{C} code.
        """
        try:
            setSearchModes = self._lib.DLL_GetSearchModes
            setSearchModes.argtypes = (POINTER(List), POINTER(SearchModes))
            setSearchModes.restype = POINTER(SearchModes)
            sm = SearchModes()
            modes_p = setSearchModes(self._list_p, byref(sm))
            modes = modes_p.contents # Dereference pointer
        except Exception, e:
            self._log.critical("Unknown error: %s", str(e))
            raise dll.APIException(e)

        return modes.search_origin, modes.search_dir

    def getCurrentIndex(self):
        """
        Get the current index value.

        The C{C} function doc string::

          unsigned long DLL_GetCurrentIndex(List *list);

          Arguments: list -- Pointer to type List
          Returns  : Current record's index

        @return: The index where the first C{Node} is 1.
        @rtype: C{int}
        @raise APIException: If a low level error occurred in the C{C} code.
        """
        try:
            getCurrentIndex = self._lib.DLL_GetCurrentIndex
            getCurrentIndex.argtypes = (POINTER(List),)
            getCurrentIndex.restype = c_ulong
            retval = getCurrentIndex(self._list_p)
        except Exception, e:
            self._log.critical("Unknown error: %s", str(e))
            raise dll.APIException(e)

        return retval

    #
    # Pointer Manipulation Methods
    #

    def currentPointerToHead(self):
        """
        Moves the current pointer to the head of the list.

        The C{C} function doc string::

          DLL_Return DLL_CurrentPointerToHead(List *list);

          Arguments: list          -- Pointer to type List
          Returns  : DLL_NORMAL    -- Record found
                     DLL_NULL_LIST -- Empty list

        @return: C{None}
        @raise APIException: If a low level error occurred in the C{C} code.
        @raise FunctionException: If the status return value is not
                                  C{Return.NORMAL}.
        """
        try:
            currentPointerToHead = self._lib.DLL_CurrentPointerToHead
            currentPointerToHead.argtypes = (POINTER(List),)
            retval = currentPointerToHead(self._list_p)
        except Exception, e:
            self._log.critical("Unknown error: %s", str(e))
            raise dll.APIException(e)

        if retval != Return.NORMAL:
            msg = "Return.%s: %s" % Return.getMessage(retval)
            raise dll.FunctionException(msg, retval=retval)

    def currentPointerToTail(self):
        """
        Moves the current pointer to the tail of the list.

        The C{C} function doc string::

          DLL_Return DLL_CurrentPointerToTail(List *list);

          Arguments: list          -- Pointer to type List
          Returns  : DLL_NORMAL    -- Record found
                     DLL_NULL_LIST -- Empty list

        @return: C{None}
        @raise APIException: If a low level error occurred in the C{C} code.
        @raise FunctionException: If the status return value is not
                                  C{Return.NORMAL}.
        """
        try:
            currentPointerToTail = self._lib.DLL_CurrentPointerToTail
            currentPointerToTail.argtypes = (POINTER(List),)
            retval = currentPointerToTail(self._list_p)
        except Exception, e:
            self._log.critical("Unknown error: %s", str(e))
            raise dll.APIException(e)

        if retval != Return.NORMAL:
            msg = "Return.%s: %s" % Return.getMessage(retval)
            raise dll.FunctionException(msg, retval=retval)

    def incrementCurrentPointer(self):
        """
        Moves the current pointer to the next C{Node}.

        The C{C} function doc string::

          DLL_Return DLL_IncrementCurrentPointer(List *list);

          Arguments: list          -- Pointer to type List
          Returns  : DLL_NORMAL    -- Record found
                     DLL_NULL_LIST -- Empty list
                     DLL_NOT_FOUND -- Record not found

        @return: C{None}
        @raise APIException: If a low level error occurred in the C{C} code.
        @raise FunctionException: If the status return value is not
                                  C{Return.NORMAL}.
        """
        try:
            incrementCurrentPointer = self._lib.DLL_IncrementCurrentPointer
            incrementCurrentPointer.argtypes = (POINTER(List),)
            retval = incrementCurrentPointer(self._list_p)
        except Exception, e:
            self._log.critical("Unknown error: %s", str(e))
            raise dll.APIException(e)

        if retval != Return.NORMAL:
            msg = "Return.%s: %s" % Return.getMessage(retval)
            raise dll.FunctionException(msg, retval=retval)

    def decrementCurrentPointer(self):
        """
        Moves the current pointer to the prior C{Node}.

        The C{C} function doc string::

          DLL_Return DLL_DecrementCurrentPointer(List *list);

          Arguments: list          -- Pointer to type List
          Returns  : DLL_NORMAL    -- Record found
                     DLL_NULL_LIST -- Empty list
                     DLL_NOT_FOUND -- Record not found

        @return: C{None}
        @raise APIException: If a low level error occurred in the C{C} code.
        @raise FunctionException: If the status return value is not
                                  C{Return.NORMAL}.
        """
        try:
            decrementCurrentPointer = self._lib.DLL_DecrementCurrentPointer
            decrementCurrentPointer.argtypes = (POINTER(List),)
            retval = decrementCurrentPointer(self._list_p)
        except Exception, e:
            self._log.critical("Unknown error: %s", str(e))
            raise dll.APIException(e)

        if retval != Return.NORMAL:
            msg = "Return.%s: %s" % Return.getMessage(retval)
            raise dll.FunctionException(msg, retval=retval)

    def storeCurrentPointer(self):
        """
        Store the current pointer in the control C{List} class.

        The C{C} function doc string::

          DLL_Return DLL_StoreCurrentPointer(List *list);

          Arguments: list          -- Pointer to type List
          Returns  : DLL_NORMAL    -- Record found
                     DLL_NOT_FOUND -- Record not found

        @return: C{None}
        @raise APIException: If a low level error occurred in the C{C} code.
        @raise FunctionException: If the status return value is not
                                  C{Return.NORMAL}.
        """
        try:
            storeCurrentPointer = self._lib.DLL_StoreCurrentPointer
            storeCurrentPointer.argtypes = (POINTER(List),)
            retval = storeCurrentPointer(self._list_p)
        except Exception, e:
            self._log.critical("Unknown error: %s", str(e))
            raise dll.APIException(e)

        if retval != Return.NORMAL:
            msg = "Return.%s: %s" % Return.getMessage(retval)
            raise dll.FunctionException(msg, retval=retval)

    def restoreCurrentPointer(self):
        """
        Restore the current pointer from the control C{List} class.

        The C{C} function doc string::

          DLL_Return DLL_restoreCurrentPointer(List *list);

          Arguments: list          -- Pointer to type List
          Returns  : DLL_NORMAL    -- Record found
                     DLL_NOT_FOUND -- Record not found

        @return: C{None}
        @raise APIException: If a low level error occurred in the C{C} code.
        @raise FunctionException: If the status return value is not
                                  C{Return.NORMAL}.
        """
        try:
            restoreCurrentPointer = self._lib.DLL_RestoreCurrentPointer
            restoreCurrentPointer.argtypes = (POINTER(List),)
            retval = restoreCurrentPointer(self._list_p)
        except Exception, e:
            self._log.critical("Unknown error: %s", str(e))
            raise dll.APIException(e)

        if retval != Return.NORMAL:
            msg = "Return.%s: %s" % Return.getMessage(retval)
            raise dll.FunctionException(msg, retval=retval)

    #
    # List Update Methods
    #

    def addRecord(self, info, pFun=None):
        """
        Adds a record to the link list. If C{pFun} is C{None} new records will
        be added at the end of the list. If the C{pFun} is a comparison function
        the added record's position in the list will be determined by this
        function.

        The C{C} function doc string::

          DLL_Return DLL_AddRecord(List *list, Info *info,
                                   int (*pFun)(Info *, Info *));

          Arguments: list          -- Pointer to type List
                     info          -- Pointer to record to add
                     pFun          -- Pointer to search function
          Returns  : DLL_NORMAL    -- Node was added successfully
                     DLL_MEM_ERROR -- Memory allocation failed

        @param info: The C{Info} class instantiated object.
        @type info: C{Info} and is defined internally as C{c_void_p}
        @keyword pFun: A C{CFUNCTYPE} object for comparing data in the user
                       C{Info} class. The default is C{None}.
        @type pFun: C{ctypes} C{CFUNCTYPE}
        @return: C{None}
        @raise APIException: If a low level error occurred in the C{C} code.
        @raise FunctionException: If status return value is not
                                  C{Return.NORMAL}.
        """
        try:
            addRecord = self._lib.DLL_AddRecord
            addRecord.argtypes = (POINTER(List), c_void_p, c_void_p,)
            retval = addRecord(self._list_p, cast(byref(info), c_void_p), pFun)
        except Exception, e:
            self._log.critical("Unknown error: %s", str(e))
            raise dll.APIException(e)

        if retval != Return.NORMAL:
            msg = "Return.%s: %s" % Return.getMessage(retval)
            raise dll.FunctionException(msg, retval=retval)

    def insertRecord(self, info, dir):
        """
        Inserts a record relative to the current pointer and is determined by
        the C{dir}. If C{dir} is C{InsertDir.ABOVE} the record will be
        inserted toward the head of the list, if C{InsertDir.BELOW} the
        record will be inserted toward the tail of the list.

        The C{C} function doc string::

          DLL_Return DLL_InsertRecord(List *list, Info *info,
                                      DLL_InsertDir dir);

          Arguments: list             -- Pointer to type List
                     info             -- Record to add
                     dir              -- Direction to insert, can be DLL_ABOVE
                                         (toward head) or DLL_BELOW (toward
                                         tail)
          Returns  : DLL_NORMAL       -- Node was added successfully
                     DLL_MEM_ERROR    -- Memory allocation failed
                     DLL_NOT_MODIFIED -- Insert direction is invalid
                                         (not DLL_ABOVE or DLL_BELOW)

        @param info: The C{Info} class instantiated object.
        @type info: C{Info} and is defined internally as C{c_void_p}
        @param dir: A value from the C{InsertDir} class.
        @type dir: C{int}
        @return: C{None}
        @raise APIException: If a low level error occurred in the C{C} code.
        @raise FunctionException: If status return value is not
                                  C{Return.NORMAL}.
        """
        try:
            insertRecord = self._lib.DLL_InsertRecord
            insertRecord.argtypes = (POINTER(List), c_void_p, c_int)
            retval = insertRecord(self._list_p, cast(byref(info), c_void_p),
                                  dir)
        except Exception, e:
            self._log.critical("Unknown error: %s", str(e))
            raise dll.APIException(e)

        if retval != Return.NORMAL:
            msg = "Return.%s: %s" % Return.getMessage(retval)
            raise dll.FunctionException(msg, retval=retval)

    def swapRecord(self, dir):
        """
        Swaps current record up or down one place in the list. The swapped
        record will still be current after completion. If C{dir} is
        C{InsertDir.ABOVE} the record will be swapped toward the head of the
        list, if C{InsertDir.BELOW} the record will be swapped toward the tail
        of the list.

        The C{C} function doc string::

          DLL_Return DLL_SwapRecord(List *list, DLL_InsertDir dir);

          Arguments: list             -- Pointer to type List
                     dir              -- Direction to swap, can be DLL_ABOVE
                                         (toward head) or DLL_BELOW (toward
                                         tail)
          Returns  : DLL_NORMAL       -- Node was swapped successfully
                     DLL_NULL_LIST    -- list->current is NULL
                     DLL_NOT_MODIFIED -- Swap direction not DLL_ABOVE or
                                         DLL_BELOW
                     DLL_NOT_FOUND    -- Current record is already at end of
                                         list indicated by dir.

        @param dir: A value from the C{InsertDir} class.
        @type dir: C{int}
        @return: C{None}
        @raise APIException: If a low level error occurred in the C{C} code.
        @raise FunctionException: If status return value is not
                                  C{Return.NORMAL}.
        """
        try:
            swapRecord = self._lib.DLL_SwapRecord
            swapRecord.argtypes = (POINTER(List), c_int)
            retval = swapRecord(self._list_p, dir)
        except Exception, e:
            self._log.critical("Unknown error: %s", str(e))
            raise dll.APIException(e)

        if retval != Return.NORMAL:
            msg = "Return.%s: %s" % Return.getMessage(retval)
            raise dll.FunctionException(msg, retval=retval)

    def updateCurrentRecord(self, record):
        """
        Updates the current record. The entire record is over written.

        The C{C} function doc string::

          DLL_Return DLL_UpdateCurrentRecord(List *list, Info *record);

          Arguments: list          -- Pointer to type List
                     record        -- Pointer to an Info structure in list
          Returns  : DLL_NORMAL    -- Record updated
                     DLL_NULL_LIST -- Empty list

        @param record: An C{Info} object with new data.
        @type record: C{Info}
        @return: C{None}
        @raise APIException: If a low level error occurred in the C{C} code.
        @raise FunctionException: If the status return value is not
                                  C{Return.NORMAL}.
        """
        try:
            updateCurrentRecord = self._lib.DLL_UpdateCurrentRecord
            updateCurrentRecord.argtypes = (POINTER(List), c_void_p,)
            retval = updateCurrentRecord(self._list_p, cast(byref(record),
                                                            c_void_p))
        except Exception, e:
            self._log.critical("Unknown error: %s", str(e))
            raise dll.APIException(e)

        if retval != Return.NORMAL:
            msg = "Return.%s: %s" % Return.getMessage(retval)
            raise dll.FunctionException(msg, retval=retval)

    def deleteCurrentRecord(self):
        """
        Delete a record from the list. This removes the C{Node} and C{Info}
        objects.

        The C{C} function doc string::

          DLL_Return DLL_DeleteCurrentRecord(List *list);

          Arguments: list          -- Pointer to type List
          Returns  : DLL_NORMAL    -- Record deleted
                     DLL_NULL_LIST -- List is empty

        @return: C{None}
        @raise APIException: If a low level error occurred in the C{C} code.
        @raise FunctionException: If the status return value is not
                                  C{Return.NORMAL}.
        """
        try:
            deleteCurrentRecord = self._lib.DLL_DeleteCurrentRecord
            deleteCurrentRecord.argtypes = (POINTER(List),)
            retval = deleteCurrentRecord(self._list_p)
        except Exception, e:
            self._log.critical("Unknown error: %s", str(e))
            raise dll.APIException(e)

        if retval != Return.NORMAL:
            msg = "Return.%s: %s" % Return.getMessage(retval)
            raise dll.FunctionException(msg, retval=retval)

    def deleteAllNodes(self):
        """
        Deletes all the C{Info} and their C{Node} objects from the list then
        reinitializes the control C{List} for continued use.

        The C{C} function doc string::

          DLL_Return DLL_DeleteEntireList(List *list);

          Arguments: list          -- Pointer to type List
          Returns  : DLL_NORMAL    -- List deleted
                     DLL_NULL_LIST -- List is empty

        @return: C{None}
        @raise APIException: If a low level error occurred in the C{C} code.
        @raise FunctionException: If the status return value is not
                                  C{Return.NORMAL}.
        """
        try:
            deleteEntireList = self._lib.DLL_DeleteEntireList
            deleteEntireList.argtypes = (POINTER(List),)
            retval = deleteEntireList(self._list_p)
        except Exception, e:
            self._log.critical("Unknown error: %s", str(e))
            raise dll.APIException(e)

        if retval != Return.NORMAL:
            msg = "Return.%s: %s" % Return.getMessage(retval)
            raise dll.FunctionException(msg, retval=retval)

    #
    # Search and Retrieval Methods
    #

    def findRecord(self, record, match, pFun=None):
        """
        Find a C{record} in the list with search criteria passed into C{match}.
        If the C{pFun} is a comparison function the found record will be
        determined by this function.

        The C{C} function doc string::

          DLL_Return DLL_FindRecord(List *list, Info *record, Info *match,
                                    int (*pFun)(Info *, Info *));

          Arguments: list              -- Pointer to type List
                     record            -- Pointer to an Info structure in list
                     match             -- Pointer to an Info structure to match
                                          to Node in list
                     pFun              -- Pointer to search function
          Returns  : DLL_NORMAL        -- Record found
                     DLL_NULL_LIST     -- Empty list
                     DLL_NOT_FOUND     -- Record not found
                     DLL_NULL_FUNCTION -- pFun is NULL

        @param record: An C{Info} object that will have the retrieved data.
        @type record: C{Info}
        @param match: An C{Info} object with the search criteria.
        @type match: C{Info}
        @keyword pFun: A C{CFUNCTYPE} object for comparing data in the user
                       C{Info} class. The default is C{None}.
        @type pFun: C{ctypes} C{CFUNCTYPE}
        @return: C{None}
        @raise APIException: If a low level error occurred in the C{C} code.
        @raise FunctionException: If the status return value is not
                                  C{Return.NORMAL}.
        """
        try:
            findRecord = self._lib.DLL_FindRecord
            findRecord.argtypes = (POINTER(List), c_void_p, c_void_p, c_void_p,)
            retval = findRecord(self._list_p, cast(byref(record), c_void_p),
                                cast(byref(match), c_void_p), pFun)
        except Exception, e:
            self._log.critical("Unknown error: %s", str(e))
            raise dll.APIException(e)

        if retval != Return.NORMAL:
            msg = "Return.%s: %s" % Return.getMessage(retval)
            raise dll.FunctionException(msg, retval=retval)

    def findNthRecord(self, record, skip):
        """
        Returns the Nth record in the list based on the setting of origin and
        direction values in the control C{List}.

        The C{C} function doc string::

          DLL_Return DLL_FindNthRecord(List *list, Info *record,
                                       unsigned long skip);

          Arguments: list          -- Pointer to type List
                     record        -- Record to hold return data
                     skip          -- Number of records to skip
                                      (Always a positive number)
          Returns  : DLL_NORMAL    -- Node was found successfully
                     DLL_NULL_LIST -- list->current is NULL
                     DLL_NOT_FOUND -- Index value is too large or wrong dir
                                      value (current record index remains
                                      unchanged)

        @param record: An C{Info} object that will have the retrieved data.
        @type record: C{Info}
        @param skip: The number of records to skip over while doing the search.
        @type skip: C{int}
        @return: C{None}
        @raise APIException: If a low level error occurred in the C{C} code.
        @raise FunctionException: If the status return value is not
                                  C{Return.NORMAL}.
        """
        try:
            findNthRecord = self._lib.DLL_FindNthRecord
            findNthRecord.argtypes = (POINTER(List), c_void_p, c_ulong,)
            retval = findNthRecord(self._list_p, cast(byref(record), c_void_p),
                                   skip)
        except Exception, e:
            self._log.critical("Unknown error: %s", str(e))
            raise dll.APIException(e)

        if retval != Return.NORMAL:
            msg = "Return.%s: %s" % Return.getMessage(retval)
            raise dll.FunctionException(msg, retval=retval)

    def getCurrentRecord(self, record):
        """
        Get the current record.

        The C{C} function doc string::

          DLL_Return DLL_GetCurrentRecord(List *list, Info *record);

          Arguments: list          -- Pointer to type List
                     record        -- Pointer to an Info structure
          Returns  : DLL_NORMAL    -- Record returned
                     DLL_NULL_LIST -- List is empty

        @param record: An C{Info} object that will have the retrieved data.
        @type record: C{Info}
        @return: C{None}
        @raise APIException: If a low level error occurred in the C{C} code.
        @raise FunctionException: If the status return value is not
                                  C{Return.NORMAL}.
        """
        try:
            getCurrentRecord = self._lib.DLL_GetCurrentRecord
            getCurrentRecord.argtypes = (POINTER(List), c_void_p,)
            retval = getCurrentRecord(self._list_p,
                                      cast(byref(record), c_void_p))
        except Exception, e:
            self._log.critical("Unknown error: %s", str(e))
            raise dll.APIException(e)

        if retval != Return.NORMAL:
            msg = "Return.%s: %s" % Return.getMessage(retval)
            raise dll.FunctionException(msg, retval=retval)

    def getPriorRecord(self, record):
        """
        Get the prior record relative to the current pointer.

        The C{C} function doc string::

          DLL_Return DLL_GetPriorRecord(List *list, Info *record);

          Arguments: list          -- Pointer to type List
                     record        -- Pointer to an Info structure
          Returns  : DLL_NORMAL    -- Record returned
                     DLL_NULL_LIST -- List is empty
                     DLL_NOT_FOUND -- Beginning of list

        @param record: An C{Info} object that will have the retrieved data.
        @type record: C{Info}
        @return: C{None}
        @raise APIException: If a low level error occurred in the C{C} code.
        @raise FunctionException: If the status return value is not
                                  C{Return.NORMAL}.
        """
        try:
            getPriorRecord = self._lib.DLL_GetPriorRecord
            getPriorRecord.argtypes = (POINTER(List), c_void_p,)
            retval = getPriorRecord(self._list_p, cast(byref(record), c_void_p))
        except Exception, e:
            self._log.critical("Unknown error: %s", str(e))
            raise dll.APIException(e)

        if retval != Return.NORMAL:
            msg = "Return.%s: %s" % Return.getMessage(retval)
            raise dll.FunctionException(msg, retval=retval)

    def getNextRecord(self, record):
        """
        Get the next record relative to the current pointer.

        The C{C} function doc string::

          DLL_Return DLL_GetNextRecord(List *list, Info *record);

          Arguments: list          -- Pointer to type List
                     record        -- Pointer to an Info structure
          Returns  : DLL_NORMAL    -- Record returned
                     DLL_NULL_LIST -- List is empty
                     DLL_NOT_FOUND -- End of list

        @param record: An C{Info} object that will have the retrieved data.
        @type record: C{Info}
        @return: C{None}
        @raise APIException: If a low level error occurred in the C{C} code.
        @raise FunctionException: If the status return value is not
                                  C{Return.NORMAL}.
        """
        try:
            getNextRecord = self._lib.DLL_GetNextRecord
            getNextRecord.argtypes = (POINTER(List), c_void_p,)
            retval = getNextRecord(self._list_p, cast(byref(record), c_void_p))
        except Exception, e:
            self._log.critical("Unknown error: %s", str(e))
            raise dll.APIException(e)

        if retval != Return.NORMAL:
            msg = "Return.%s: %s" % Return.getMessage(retval)
            raise dll.FunctionException(msg, retval=retval)

    #
    # Input/Output Methods
    #

    def saveList(self, path):
        """
        Save list to disk. The file is saved in binary format because the fields
        in the C{Info} class are save in their entirety causing C{NULL} bytes
        to be padded after text. It should be trivial to pad the fields with
        spaces before calling this method thus eliminating any binary data
        in text files.

        The C{C} function doc string::

          DLL_Return DLL_SaveList(List *list, const char *path);

          Arguments: list             -- Pointer to type List
                     path             -- Pointer to path and filename
          Return   : DLL_NORMAL       -- File written successfully
                     DLL_NULL_LIST    -- List is empty
                     DLL_OPEN_ERROR   -- File open error
                     DLL_WRITE_ERROR  -- File write error
                     DLL_NOT_MODIFIED -- Unmodified list no save was done

        @param path: The full path to the data file.
        @type path: C{str}
        @return: C{None}
        @raise APIException: If a low level error occurred in the C{C} code.
        @raise FunctionException: If the status return value is not
                                  C{Return.NORMAL}.
        """
        try:
            saveList = self._lib.DLL_SaveList
            saveList.argtypes = (POINTER(List), c_char_p,)
            retval = saveList(self._list_p, c_char_p(path))
        except Exception, e:
            self._log.critical("Unknown error: %s", str(e))
            raise dll.APIException(e)

        if retval != Return.NORMAL:
            msg = "Return.%s: %s" % Return.getMessage(retval)
            raise dll.FunctionException(msg, retval=retval)

    def loadList(self, path, pFun=None):
        """
        Load list to disk. When using the C{pFun} keyword argument the function
        passed will sort the incoming data.

        The C{C} function doc string::

          DLL_Return DLL_LoadList(List *list, const char *path,
                                  int (*pFun)(Info *, Info *));

          Arguments: list           -- Pointer to type List
                     path           -- Pointer to path and filename
                     pFun           -- Pointer to search function
          Return   : DLL_NORMAL     -- File written successfully
                     DLL_MEM_ERROR  -- Memory allocation failed
                     DLL_OPEN_ERROR -- File open error
                     DLL_READ_ERROR -- File read error

        @return: C{None}
        @raise APIException: If a low level error occurred in the C{C} code.
        @raise FunctionException: If the status return value is not
                                  C{Return.NORMAL}.
        """
        try:
            loadList = self._lib.DLL_LoadList
            loadList.argtypes = (POINTER(List), c_char_p, c_void_p,)
            retval = loadList(self._list_p, c_char_p(path), pFun)
        except Exception, e:
            self._log.critical("Unknown error: %s", str(e))
            raise dll.APIException(e)

        if retval != Return.NORMAL:
            msg = "Return.%s: %s" % Return.getMessage(retval)
            raise dll.FunctionException(msg, retval=retval)

    def compare(self):
        """
        A basic compare function. You may need to write your own.

        @return: The results will be one of C{< 0}, C{0}, or C{> 0}.
        """
        # Create a prototype function for the compare function.
        #cmpField(c_char_p("abcde"), c_char_p("bcdef"))
        cmpPrototype = CFUNCTYPE(c_int, c_char_p, c_char_p)
        return cmpPrototype(cmp)
