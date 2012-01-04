#
# dlinklist/linklist.py
#
# ctypes wrappers for the Doubly Linked list API.
#
# $Author$
# $Date$
# $Revision$
#

import logging
from ctypes import CDLL, CFUNCTYPE, POINTER, Structure, byref, cast, \
     string_at, c_void_p, c_int, c_ulong, c_bool, c_size_t, c_char_p


import dlinklist as dll


class Return(object):
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
        return (self._ERRORS.get(num, num),
                self.__MESSAGES.get(num, "Unknown error"))

Return._ERRORS = dict([(v,k) for k,v in Return.__dict__.items()
                       if not k.startswith("_")])


class SrchOrigin(object):
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
        return (self._ORIGINS.get(num, num),
                self.__MESSAGES.get(num, "Unknown search origin"))

SrchOrigin._ORIGINS = dict([(v,k) for k,v in SrchOrigin.__dict__.items()
                            if not k.startswith("_")])


class SrchDir(object):
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
        return (self._DIRS.get(num, num),
                self.__MESSAGES.get(num, "Unknown search direction"))

SrchDir._DIRS = dict([(v,k) for k,v in SrchDir.__dict__.items()
                      if not k.startswith("_")])


class InsertDir(object):
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
        return (self._DIRS.get(num, num),
                self.__MESSAGES.get(num, "Unknown search direction"))

InsertDir._DIRS = dict([(v,k) for k,v in InsertDir.__dict__.items()
                        if not k.startswith("_")])


class Node(Structure):
    _fields_ = [
        ('info', c_void_p),
        ]
Node._fields_.append([('next', POINTER(Node)),
                      ('prior', POINTER(Node))])


class List(Structure):
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
    _fields_ = (
        ('search_origin', c_int),
        ('search_dir', c_int),
        )


class DLinklist(object):
    __LIBRARY = ("./libdll.so", dll._RES_PATH, "../src/libdll.so",)

    def __init__(self, logname="", disableLogging=False):
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
            lib = self.__LIBRARY[0][2:]
            msg = "Could not load library: %s"
            self._log.critical(msg, lib)
            raise dll.LibraryNotFoundException(msg % lib)

    def create(self, infoSize):
        list_p = self.createList()
        return self.initialize(list_p, infoSize)

    def createList(self):
        """
        List *DLL_CreateList(List **list);

        Arguments: list -- Pointer to a pointer to a name of a structure to
                           create.
        Returns  : Pointer to created structure NULL if unsuccessful
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
        return list_p

    def initialize(self, list_p, infoSize):
        """
        DLL_Return DLL_InitializeList(List *list, size_t infosize);

        Arguments: list          -- Pointer to type List
                   infosize      -- Size of user Info
        Returns  : DLL_NORMAL    -- Initialization was done successfully
                   DLL_ZERO_INFO -- sizeof(Info) is zero
                   DLL_NULL_LIST -- Info is NULL
        """
        try:
            initList = self._lib.DLL_InitializeList
            initList.argtypes = (POINTER(List), c_size_t)
            retval = initList(list_p, c_size_t(infoSize))
        except Exception, e:
            self._log.critical("Unknown error: %s", str(e))
            raise dll.APIException(e)

        if retval != Return.NORMAL:
            msg = "Return.%s: %s" % Return.getMessage(retval)
            raise dll.FunctionException(msg, retval=retval)

        return list_p

    def destroy(self, list_p):
        """
        void DLL_DestroyList(List **list);

        Arguments: list -- Pointer to a pointer to a name of a structure to
                           destroy.
        Returns  : void
        """
        try:
            destroyList = self._lib.DLL_DestroyList
            destroyList.argtypes = (POINTER(POINTER(List)),)
            destroyList.restype = None
            destroyList(byref(list_p))
        except Exception, e:
            self._log.critical("Unknown error: %s", str(e))
            raise dll.APIException(e)

    def isListEmpty(self, list_p):
        """
        DLL_Boolean DLL_IsListEmpty(List *list);

        Arguments: list      -- Pointer to type List
        Returns  : DLL_TRUE  -- List is empty
                   DLL_FALSE -- List has items in it
        """
        try:
            isListEmpty = self._lib.DLL_IsListEmpty
            isListEmpty.argtypes = (POINTER(List),)
            retval = isListEmpty(list_p)
        except Exception, e:
            self._log.critical("Unknown error: %s", str(e))
            raise dll.APIException(e)

        return retval

    def isListFull(self, list_p):
        """
        DLL_Boolean DLL_IsListFull(List *list);

        Arguments: list      -- Pointer to type List
        Returns  : DLL_TRUE  -- List is full (memory dependent)
                   DLL_FALSE -- List is empty or partially full
        """
        try:
            isListFull = self._lib.DLL_IsListFull
            isListFull.argtypes = (POINTER(List),)
            retval = isListFull(list_p)
        except Exception, e:
            self._log.critical("Unknown error: %s", str(e))
            raise dll.APIException(e)

        return retval

    def getNumberOfRecords(self, list_p):
        """
        unsigned long DLL_GetNumberOfRecords(List *list);

        Arguments: list -- Pointer to type List
        Returns  : Number of records in list
        """
        try:
            getNumberOfRecords = self._lib.DLL_GetNumberOfRecords
            getNumberOfRecords.argtypes = (POINTER(List),)
            retval = getNumberOfRecords(list_p)
        except Exception, e:
            self._log.critical("Unknown error: %s", str(e))
            raise dll.APIException(e)

        return retval

    def setSearchModes(self, list_p, origin, dir):
        """
        DLL_Return DLL_SetSearchModes(List *list, DLL_SrchOrigin origin,
                                      DLL_SrchDir dir);

        Arguments: list             -- Pointer to type List
                   origin           -- Indicates the start search pointer to use
                   dir              -- Indicates the direction to search in
        Returns  : DLL_NORMAL       -- Values assigned were accepted
                   DLL_NOT_MODIFIED -- Values were not assigned--invalid type
                                       (defaults are still in place)
        """
        try:
            setSearchModes = self._lib.DLL_SetSearchModes
            setSearchModes.argtypes = (POINTER(List), c_int, c_int)
            retval = setSearchModes(list_p, origin, dir)
        except Exception, e:
            self._log.critical("Unknown error: %s", str(e))
            raise dll.APIException(e)

        if retval != Return.NORMAL:
            msg = "Return.%s: %s" % Return.getMessage(retval)
            raise dll.FunctionException(msg, retval=retval)

    def getSearchModes(self, list_p, sm):
        """
        DLL_SearchModes DLL_GetSearchModes(List *list, DLL_SearchModes *ssp);

        Arguments: list -- Pointer to type List
                   ssp  -- Save structure pointer
        Returns  : Pointer to type DLL_SearchModes
        """
        try:
            setSearchModes = self._lib.DLL_GetSearchModes
            setSearchModes.argtypes = (POINTER(List), POINTER(SearchModes))
            setSearchModes.restype = POINTER(SearchModes)
            modes_p = setSearchModes(list_p, byref(sm))
            modes = modes_p.contents # Dereference pointer
        except Exception, e:
            self._log.critical("Unknown error: %s", str(e))
            raise dll.APIException(e)

        return modes

    def getCurrentIndex(self, list_p):
        """
        unsigned long DLL_GetCurrentIndex(List *list);

        Arguments: list -- Pointer to type List
        Returns  : Current record's index
        """
        try:
            getCurrentIndex = self._lib.DLL_GetCurrentIndex
            getCurrentIndex.argtypes = (POINTER(List),)
            getCurrentIndex.restype = c_ulong
            retval = getCurrentIndex(list_p)
        except Exception, e:
            self._log.critical("Unknown error: %s", str(e))
            raise dll.APIException(e)

        return retval

    def currentPointerToHead(self, list_p):
        """
        DLL_Return DLL_CurrentPointerToHead(List *list);

        Arguments: list          -- Pointer to type List
        Returns  : DLL_NORMAL    -- Record found
                   DLL_NULL_LIST -- Empty list
        """
        try:
            currentPointerToHead = self._lib.DLL_CurrentPointerToHead
            currentPointerToHead.argtypes = (POINTER(List),)
            retval = currentPointerToHead(list_p)
        except Exception, e:
            self._log.critical("Unknown error: %s", str(e))
            raise dll.APIException(e)

        if retval != Return.NORMAL:
            msg = "Return.%s: %s" % Return.getMessage(retval)
            raise dll.FunctionException(msg, retval=retval)

    def currentPointerToTail(self, list_p):
        """
        DLL_Return DLL_CurrentPointerToTail(List *list);

        Arguments: list          -- Pointer to type List
        Returns  : DLL_NORMAL    -- Record found
                   DLL_NULL_LIST -- Empty list
        """
        try:
            currentPointerToTail = self._lib.DLL_CurrentPointerToTail
            currentPointerToTail.argtypes = (POINTER(List),)
            retval = currentPointerToTail(list_p)
        except Exception, e:
            self._log.critical("Unknown error: %s", str(e))
            raise dll.APIException(e)

        if retval != Return.NORMAL:
            msg = "Return.%s: %s" % Return.getMessage(retval)
            raise dll.FunctionException(msg, retval=retval)

    def incrementCurrentPointer(self, list_p):
        """
        DLL_Return DLL_IncrementCurrentPointer(List *list);

        Arguments: list          -- Pointer to type List
        Returns  : DLL_NORMAL    -- Record found
                   DLL_NULL_LIST -- Empty list
                   DLL_NOT_FOUND -- Record not found
        """
        try:
            incrementCurrentPointer = self._lib.DLL_IncrementCurrentPointer
            incrementCurrentPointer.argtypes = (POINTER(List),)
            retval = incrementCurrentPointer(list_p)
        except Exception, e:
            self._log.critical("Unknown error: %s", str(e))
            raise dll.APIException(e)

        if retval != Return.NORMAL:
            msg = "Return.%s: %s" % Return.getMessage(retval)
            raise dll.FunctionException(msg, retval=retval)

    def decrementCurrentPointer(self, list_p):
        """
        DLL_Return DLL_DecrementCurrentPointer(List *list);

        Arguments: list          -- Pointer to type List
        Returns  : DLL_NORMAL    -- Record found
                   DLL_NULL_LIST -- Empty list
                   DLL_NOT_FOUND -- Record not found
        """
        try:
            decrementCurrentPointer = self._lib.DLL_DecrementCurrentPointer
            decrementCurrentPointer.argtypes = (POINTER(List),)
            retval = decrementCurrentPointer(list_p)
        except Exception, e:
            self._log.critical("Unknown error: %s", str(e))
            raise dll.APIException(e)

        if retval != Return.NORMAL:
            msg = "Return.%s: %s" % Return.getMessage(retval)
            raise dll.FunctionException(msg, retval=retval)

    def storeCurrentPointer(self, list_p):
        """
        DLL_Return DLL_StoreCurrentPointer(List *list);

        Arguments: list          -- Pointer to type List
        Returns  : DLL_NORMAL    -- Record found
                   DLL_NOT_FOUND -- Record not found
        """
        try:
            storeCurrentPointer = self._lib.DLL_StoreCurrentPointer
            storeCurrentPointer.argtypes = (POINTER(List),)
            retval = storeCurrentPointer(list_p)
        except Exception, e:
            self._log.critical("Unknown error: %s", str(e))
            raise dll.APIException(e)

        if retval != Return.NORMAL:
            msg = "Return.%s: %s" % Return.getMessage(retval)
            raise dll.FunctionException(msg, retval=retval)

    def restoreCurrentPointer(self, list_p):
        """
        DLL_Return DLL_restoreCurrentPointer(List *list);

        Arguments: list          -- Pointer to type List
        Returns  : DLL_NORMAL    -- Record found
                   DLL_NOT_FOUND -- Record not found
        """
        try:
            restoreCurrentPointer = self._lib.DLL_RestoreCurrentPointer
            restoreCurrentPointer.argtypes = (POINTER(List),)
            retval = restoreCurrentPointer(list_p)
        except Exception, e:
            self._log.critical("Unknown error: %s", str(e))
            raise dll.APIException(e)

        if retval != Return.NORMAL:
            msg = "Return.%s: %s" % Return.getMessage(retval)
            raise dll.FunctionException(msg, retval=retval)

    def addRecord(self, list_p, info, pFun=None):
        """
        DLL_Return DLL_AddRecord(List *list, Info *info,
                                 int (*pFun)(Info *, Info *));

        Arguments: list          -- Pointer to type List
                   info          -- Pointer to record to add
                   pFun          -- Pointer to search function
        Returns  : DLL_NORMAL    -- Node was added successfully
                   DLL_MEM_ERROR -- Memory allocation failed
        """
        try:
            addRecord = self._lib.DLL_AddRecord
            addRecord.argtypes = (POINTER(List), c_void_p, c_void_p,)
            retval = addRecord(list_p, cast(byref(info), c_void_p), pFun)
        except Exception, e:
            self._log.critical("Unknown error: %s", str(e))
            raise dll.APIException(e)

        if retval != Return.NORMAL:
            msg = "Return.%s: %s" % Return.getMessage(retval)
            raise dll.FunctionException(msg, retval=retval)

    def insertRecord(self, list_p, info, dir):
        """
        DLL_Return DLL_InsertRecord(List *list, Info *info, DLL_InsertDir dir);

        Arguments: list             -- Pointer to type List
                   info             -- Record to add
                   dir              -- Direction to insert, can be DLL_ABOVE
                                       (toward head) or DLL_BELOW (toward tail)
        Returns  : DLL_NORMAL       -- Node was added successfully
                   DLL_MEM_ERROR    -- Memory allocation failed
                   DLL_NOT_MODIFIED -- Insert direction is invalid
                                       (not DLL_ABOVE or DLL_BELOW)
        """
        try:
            insertRecord = self._lib.DLL_InsertRecord
            insertRecord.argtypes = (POINTER(List), c_void_p, c_int)
            retval = insertRecord(list_p, cast(byref(info), c_void_p), dir)
        except Exception, e:
            self._log.critical("Unknown error: %s", str(e))
            raise dll.APIException(e)

        if retval != Return.NORMAL:
            msg = "Return.%s: %s" % Return.getMessage(retval)
            raise dll.FunctionException(msg, retval=retval)

    def swapRecord(self, list_p, dir):
        """
        DLL_Return DLL_SwapRecord(List *list, DLL_InsertDir dir);

        Arguments: list             -- Pointer to type List
                   dir              -- Direction to swap, can be DLL_ABOVE
                                       (toward head) or DLL_BELOW (toward tail)
        Returns  : DLL_NORMAL       -- Node was swaped successfully
                   DLL_NULL_LIST    -- list->current is NULL
                   DLL_NOT_MODIFIED -- Swap direction not DLL_ABOVE or DLL_BELOW
                   DLL_NOT_FOUND    -- Current record is already at end of
                                       list indicated by dir.
        """
        try:
            swapRecord = self._lib.DLL_SwapRecord
            swapRecord.argtypes = (POINTER(List), c_int)
            retval = swapRecord(list_p, dir)
        except Exception, e:
            self._log.critical("Unknown error: %s", str(e))
            raise dll.APIException(e)

        if retval != Return.NORMAL:
            msg = "Return.%s: %s" % Return.getMessage(retval)
            raise dll.FunctionException(msg, retval=retval)

    def updateCurrentRecord(self, list_p, record):
        """
        DLL_Return DLL_UpdateCurrentRecord(List *list, Info *record);

        Arguments: list          -- Pointer to type List
                   record        -- Pointer to an Info structure in list
        Returns  : DLL_NORMAL    -- Record updated
                   DLL_NULL_LIST -- Empty list
        """
        try:
            updateCurrentRecord = self._lib.DLL_UpdateCurrentRecord
            updateCurrentRecord.argtypes = (POINTER(List), c_void_p,)
            retval = updateCurrentRecord(list_p, cast(byref(record), c_void_p))
        except Exception, e:
            self._log.critical("Unknown error: %s", str(e))
            raise dll.APIException(e)

        if retval != Return.NORMAL:
            msg = "Return.%s: %s" % Return.getMessage(retval)
            raise dll.FunctionException(msg, retval=retval)

    def deleteCurrentRecord(self, list_p):
        """
        DLL_Return DLL_DeleteCurrentRecord(List *list);

        Arguments: list          -- Pointer to type List
        Returns  : DLL_NORMAL    -- Record deleted
                   DLL_NULL_LIST -- List is empty
        """
        try:
            deleteCurrentRecord = self._lib.DLL_DeleteCurrentRecord
            deleteCurrentRecord.argtypes = (POINTER(List),)
            retval = deleteCurrentRecord(list_p)
        except Exception, e:
            self._log.critical("Unknown error: %s", str(e))
            raise dll.APIException(e)

        if retval != Return.NORMAL:
            msg = "Return.%s: %s" % Return.getMessage(retval)
            raise dll.FunctionException(msg, retval=retval)

    def deleteAllNodes(self, list_p):
        """
        DLL_Return DLL_DeleteEntireList(List *list);

        Arguments: list          -- Pointer to type List
        Returns  : DLL_NORMAL    -- List deleted
                   DLL_NULL_LIST -- List is empty
        """
        try:
            deleteEntireList = self._lib.DLL_DeleteEntireList
            deleteEntireList.argtypes = (POINTER(List),)
            retval = deleteEntireList(list_p)
        except Exception, e:
            self._log.critical("Unknown error: %s", str(e))
            raise dll.APIException(e)

        if retval != Return.NORMAL:
            msg = "Return.%s: %s" % Return.getMessage(retval)
            raise dll.FunctionException(msg, retval=retval)

    def findRecord(self, list_p, record, match, pFun=None):
        """
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
        """
        try:
            findRecord = self._lib.DLL_FindRecord
            findRecord.argtypes = (POINTER(List), c_void_p, c_void_p, c_void_p,)
            retval = findRecord(list_p, cast(byref(record), c_void_p),
                                cast(byref(match), c_void_p), pFun)
        except Exception, e:
            self._log.critical("Unknown error: %s", str(e))
            raise dll.APIException(e)

        if retval != Return.NORMAL:
            msg = "Return.%s: %s" % Return.getMessage(retval)
            raise dll.FunctionException(msg, retval=retval)

    def findNthRecord(self, list_p, record, skip):
        """
        DLL_Return DLL_FindNthRecord(List *list, Info *record,
                                     unsigned long skip);

        Arguments: list          -- Pointer to type List
                   record        -- Record to hold return data
                   skip          -- Number of records to skip
                                    (Always a positive number)
        Returns  : DLL_NORMAL    -- Node was found successfully
                   DLL_NULL_LIST -- list->current is NULL
                   DLL_NOT_FOUND -- Index value is too large or wrong dir value
                                    (current record index remains unchanged)
        """
        try:
            findNthRecord = self._lib.DLL_FindNthRecord
            findNthRecord.argtypes = (POINTER(List), c_void_p, c_ulong,)
            retval = findNthRecord(list_p, cast(byref(record), c_void_p), skip)
        except Exception, e:
            self._log.critical("Unknown error: %s", str(e))
            raise dll.APIException(e)

        if retval != Return.NORMAL:
            msg = "Return.%s: %s" % Return.getMessage(retval)
            raise dll.FunctionException(msg, retval=retval)

    def getCurrentRecord(self, list_p, record):
        """
        DLL_Return DLL_GetCurrentRecord(List *list, Info *record);

        Arguments: list          -- Pointer to type List
                   record        -- Pointer to an Info structure
        Returns  : DLL_NORMAL    -- Record returned
                   DLL_NULL_LIST -- List is empty
        """
        try:
            getCurrentRecord = self._lib.DLL_GetCurrentRecord
            getCurrentRecord.argtypes = (POINTER(List), c_void_p,)
            retval = getCurrentRecord(list_p, cast(byref(record), c_void_p))
        except Exception, e:
            self._log.critical("Unknown error: %s", str(e))
            raise dll.APIException(e)

        if retval != Return.NORMAL:
            msg = "Return.%s: %s" % Return.getMessage(retval)
            raise dll.FunctionException(msg, retval=retval)

    def getPriorRecord(self, list_p, record):
        """
        DLL_Return DLL_GetPriorRecord(List *list, Info *record);

        Arguments: list          -- Pointer to type List
                   record        -- Pointer to an Info structure
        Returns  : DLL_NORMAL    -- Record returned
                   DLL_NULL_LIST -- List is empty
                   DLL_NOT_FOUND -- Beginning of list
        """
        try:
            getPriorRecord = self._lib.DLL_GetPriorRecord
            getPriorRecord.argtypes = (POINTER(List), c_void_p,)
            retval = getPriorRecord(list_p, cast(byref(record), c_void_p))
        except Exception, e:
            self._log.critical("Unknown error: %s", str(e))
            raise dll.APIException(e)

        if retval != Return.NORMAL:
            msg = "Return.%s: %s" % Return.getMessage(retval)
            raise dll.FunctionException(msg, retval=retval)

    def getNextRecord(self, list_p, record):
        """
        DLL_Return DLL_GetNextRecord(List *list, Info *record);

        Arguments: list          -- Pointer to type List
                   record        -- Pointer to an Info structure
        Returns  : DLL_NORMAL    -- Record returned
                   DLL_NULL_LIST -- List is empty
                   DLL_NOT_FOUND -- End of list
        """
        try:
            getNextRecord = self._lib.DLL_GetNextRecord
            getNextRecord.argtypes = (POINTER(List), c_void_p,)
            retval = getNextRecord(list_p, cast(byref(record), c_void_p))
        except Exception, e:
            self._log.critical("Unknown error: %s", str(e))
            raise dll.APIException(e)

        if retval != Return.NORMAL:
            msg = "Return.%s: %s" % Return.getMessage(retval)
            raise dll.FunctionException(msg, retval=retval)

    def saveList(self, list_p, path):
        """
        DLL_Return DLL_SaveList(List *list, const char *path);

        Arguments: list             -- Pointer to type List
                   path             -- Pointer to path and filename
        Return   : DLL_NORMAL       -- File written successfully
                   DLL_NULL_LIST    -- List is empty
                   DLL_OPEN_ERROR   -- File open error
                   DLL_WRITE_ERROR  -- File write error
                   DLL_NOT_MODIFIED -- Unmodified list no save was done
        """
        try:
            saveList = self._lib.DLL_SaveList
            saveList.argtypes = (POINTER(List), c_char_p,)
            retval = saveList(list_p, c_char_p(path))
        except Exception, e:
            self._log.critical("Unknown error: %s", str(e))
            raise dll.APIException(e)

        if retval != Return.NORMAL:
            msg = "Return.%s: %s" % Return.getMessage(retval)
            raise dll.FunctionException(msg, retval=retval)

    def loadList(self, list_p, path, pFun=None):
        """
        DLL_Return DLL_LoadList(List *list, const char *path,
                                int (*pFun)(Info *, Info *));

        Arguments: list           -- Pointer to type List
                   path           -- Pointer to path and filename
                   pFun           -- Pointer to search function
        Return   : DLL_NORMAL     -- File written successfully
                   DLL_MEM_ERROR  -- Memory allocation failed
                   DLL_OPEN_ERROR -- File open error
                   DLL_READ_ERROR -- File read error
        """
        try:
            loadList = self._lib.DLL_LoadList
            loadList.argtypes = (POINTER(List), c_char_p, c_void_p,)
            retval = loadList(list_p, c_char_p(path), pFun)
        except Exception, e:
            self._log.critical("Unknown error: %s", str(e))
            raise dll.APIException(e)

        if retval != Return.NORMAL:
            msg = "Return.%s: %s" % Return.getMessage(retval)
            raise dll.FunctionException(msg, retval=retval)

    def version(self):
        """
        DLL_Version() : Returns a pointer to version information

        Arguments: void

        Return   : char * -- Pointer to version info
        """
        try:
            version = string_at(self._lib.DLL_Version())
        except Exception, e:
            self._log.critical("Unknown error: %s", str(e))
            raise dll.APIException(e)

        return version

    def compare(self):
        # Create a prototype function for the compare function.
        #cmpField(c_char_p("abcde"), c_char_p("bcdef"))
        cmpPrototype = CFUNCTYPE(c_int, c_char_p, c_char_p)
        return cmpPrototype(cmp)
