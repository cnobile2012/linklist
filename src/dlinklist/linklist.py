#
# ctypes wrapper for the Doubly Linked list API.
#
# $Author$
# $Date$
# $Revision$
#

import logging
from ctypes import *


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

    def __init__(self, logname="DLinkList"):
        pass

    def _initList(self):
        """
        List *DLL_CreateList(List **list);

        Arguments: list -- Pointer to a pointer to a name of a structure to
                           create.
        Returns  : Pointer to created structure NULL if unsuccessful


        DLL_Return DLL_InitializeList(List *list, size_t infosize);

        Arguments: list          -- Pointer to type List
                   infosize      -- Size of user Info
        Returns  : DLL_NORMAL    -- Initialization was done successfully
                   DLL_ZERO_INFO -- sizeof(Info) is zero
                   DLL_NULL_LIST -- Info is NULL
        """
        createList = self._lib.DLL_CreateList
        createList.argtypes = (POINTER(POINTER(List)),)
        createList.restype = POINTER(List)
        control = POINTER(List)()
        list_p = createList(byref(control))

        msg = "DLL_CreateList failed, list_p: %s."
        self.assertTrue(list_p not in (0, None),
                        msg=msg % hex(cast(list_p, c_void_p).value))

        initList = self._lib.DLL_InitializeList
        initList.argtypes = (POINTER(List), c_size_t)
        retval = initList(list_p, c_size_t(sizeof(Info)))

        msg = "Return.%s: %s" % Return.getMessage(retval)
        self.assertTrue(retval == Return.NORMAL, msg=msg)

        return list_p

    def _destroyList(self, list_p):
        """
        void DLL_DestroyList(List **list);

        Arguments: list -- Pointer to a pointer to a name of a structure to
                           destroy.
        Returns  : void
        """
        destroyList = self._lib.DLL_DestroyList
        destroyList.argtypes = (POINTER(POINTER(List)),)
        destroyList.restype = None
        destroyList(byref(list_p))

    def _isListEmpty(self, list_p, test=True):
        """
        DLL_Boolean DLL_IsListEmpty(List *list);

        Arguments: list          -- Pointer to type List
        Returns  : DLL_TRUE  -- List is empty
                   DLL_FALSE -- List has items in it
        """
        isListEmpty = self._lib.DLL_IsListEmpty
        isListEmpty.argtypes = (POINTER(List),)
        retval = isListEmpty(list_p)

        msg = "retval: %s, test: %s"
        self.assertTrue(retval == test, msg=msg % (retval, test))

    def _isListFull(self, list_p, test=True):
        """
        DLL_Boolean DLL_IsListFull(List *list);

        Arguments: list      -- Pointer to type List
        Returns  : DLL_TRUE  -- List is full (memory dependent)
                   DLL_FALSE -- List is empty or partially full
        """
        isListFull = self._lib.DLL_IsListFull
        isListFull.argtypes = (POINTER(List),)
        retval = isListFull(list_p)

        msg = "retval: %s, test: %s"
        self.assertTrue(retval == test, msg=msg % (retval, test))

    def _getNumberOfRecords(self, list_p, test=0):
        """
        unsigned long DLL_GetNumberOfRecords(List *list);

        Arguments: list -- Pointer to type List
        Returns  : Number of records in list
        """
        getNumberOfRecords = self._lib.DLL_GetNumberOfRecords
        getNumberOfRecords.argtypes = (POINTER(List),)
        retval = getNumberOfRecords(list_p)

        msg = "retval: %s, test: %s"
        self.assertTrue(retval == test, msg=msg % (retval, test))

    def _setSearchModes(self, list_p, origin, dir, result=Return.NORMAL):
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
        setSearchModes = self._lib.DLL_SetSearchModes
        setSearchModes.argtypes = (POINTER(List), c_int, c_int)
        retval = setSearchModes(list_p, origin, dir)

        msg = "Return.%s: %s" % Return.getMessage(retval)
        self.assertTrue(retval == result, msg=msg)

    def _getSearchModes(self, list_p, sm, test=(SrchOrigin.HEAD, SrchDir.DOWN)):
        """
        DLL_SearchModes DLL_GetSearchModes(List *list, DLL_SearchModes *ssp);

        Arguments: list -- Pointer to type List
                   ssp  -- Save structure pointer
        Returns  : Pointer to type DLL_SearchModes
        """
        setSearchModes = self._lib.DLL_GetSearchModes
        setSearchModes.argtypes = (POINTER(List), POINTER(SearchModes))
        setSearchModes.restype = POINTER(SearchModes)
        modes_p = setSearchModes(list_p, byref(sm))
        modes = modes_p.contents # Dereference pointer

        msg = "SrchOrigin.%s: %s" % SrchOrigin.getMessage(modes.search_origin)
        self.assertTrue(modes.search_origin == test[0], msg=msg)
        msg = "SrchDir.%s: %s" % SrchDir.getMessage(modes.search_dir)
        self.assertTrue(modes.search_dir == test[1], msg=msg)

    def _getCurrentIndex(self, list_p, test=0):
        """
        unsigned long DLL_GetCurrentIndex(List *list);

        Arguments: list -- Pointer to type List
        Returns  : Current record's index
        """
        getCurrentIndex = self._lib.DLL_GetCurrentIndex
        getCurrentIndex.argtypes = (POINTER(List),)
        getCurrentIndex.restype = c_ulong
        retval = getCurrentIndex(list_p)

        msg = "retval: %s, test: %s"
        self.assertTrue(retval == test, msg=msg % (retval, test))

    def _currentPointerToHead(self, list_p, result=Return.NORMAL):
        """
        DLL_Return DLL_CurrentPointerToHead(List *list);

        Arguments: list          -- Pointer to type List
        Returns  : DLL_NORMAL    -- Record found
                   DLL_NULL_LIST -- Empty list
        """
        currentPointerToHead = self._lib.DLL_CurrentPointerToHead
        currentPointerToHead.argtypes = (POINTER(List),)
        retval = currentPointerToHead(list_p)

        msg = "Return.%s: %s" % Return.getMessage(retval)
        self.assertTrue(retval == result, msg=msg)

    def _currentPointerToTail(self, list_p, result=Return.NORMAL):
        """
        DLL_Return DLL_CurrentPointerToTail(List *list);

        Arguments: list          -- Pointer to type List
        Returns  : DLL_NORMAL    -- Record found
                   DLL_NULL_LIST -- Empty list
        """
        currentPointerToTail = self._lib.DLL_CurrentPointerToTail
        currentPointerToTail.argtypes = (POINTER(List),)
        retval = currentPointerToTail(list_p)

        msg = "Return.%s: %s" % Return.getMessage(retval)
        self.assertTrue(retval == result, msg=msg)

    def _incrementCurrentPointer(self, list_p, result=Return.NORMAL):
        """
        DLL_Return DLL_IncrementCurrentPointer(List *list);

        Arguments: list          -- Pointer to type List
        Returns  : DLL_NORMAL    -- Record found
                   DLL_NULL_LIST -- Empty list
                   DLL_NOT_FOUND -- Record not found
        """
        incrementCurrentPointer = self._lib.DLL_IncrementCurrentPointer
        incrementCurrentPointer.argtypes = (POINTER(List),)
        retval = incrementCurrentPointer(list_p)

        msg = "Return.%s: %s" % Return.getMessage(retval)
        self.assertTrue(retval == result, msg=msg)

    def _decrementCurrentPointer(self, list_p, result=Return.NORMAL):
        """
        DLL_Return DLL_DecrementCurrentPointer(List *list);

        Arguments: list          -- Pointer to type List
        Returns  : DLL_NORMAL    -- Record found
                   DLL_NULL_LIST -- Empty list
                   DLL_NOT_FOUND -- Record not found
        """
        decrementCurrentPointer = self._lib.DLL_DecrementCurrentPointer
        decrementCurrentPointer.argtypes = (POINTER(List),)
        retval = decrementCurrentPointer(list_p)

        msg = "%s: %s" % Return.getMessage(retval)
        self.assertTrue(retval == result, msg=msg)

    def _storeCurrentPointer(self, list_p, result=Return.NORMAL):
        """
        DLL_Return DLL_StoreCurrentPointer(List *list);

        Arguments: list          -- Pointer to type List
        Returns  : DLL_NORMAL    -- Record found
                   DLL_NOT_FOUND -- Record not found
        """
        storeCurrentPointer = self._lib.DLL_StoreCurrentPointer
        storeCurrentPointer.argtypes = (POINTER(List),)
        retval = storeCurrentPointer(list_p)

        msg = "Return.%s: %s" % Return.getMessage(retval)
        self.assertTrue(retval == result, msg=msg)

    def _restoreCurrentPointer(self, list_p, result=Return.NORMAL):
        """
        DLL_Return DLL_restoreCurrentPointer(List *list);

        Arguments: list          -- Pointer to type List
        Returns  : DLL_NORMAL    -- Record found
                   DLL_NOT_FOUND -- Record not found
        """
        restoreCurrentPointer = self._lib.DLL_RestoreCurrentPointer
        restoreCurrentPointer.argtypes = (POINTER(List),)
        retval = restoreCurrentPointer(list_p)

        msg = "Return.%s: %s" % Return.getMessage(retval)
        self.assertTrue(retval == result, msg=msg)

    def _addRecord(self, list_p, info, pFun=None, result=Return.NORMAL):
        """
        DLL_Return DLL_AddRecord(List *list, Info *info,
                                 int (*pFun)(Info *, Info *));

        Arguments: list          -- Pointer to type List
                   info          -- Pointer to record to add
                   pFun          -- Pointer to search function
        Returns  : DLL_NORMAL    -- Node was added successfully
                   DLL_MEM_ERROR -- Memory allocation failed
        """
        addRecord = self._lib.DLL_AddRecord
        addRecord.argtypes = (POINTER(List), POINTER(Info), c_void_p,)
        retval = addRecord(list_p, info, pFun)

        msg = "Return.%s: %s" % Return.getMessage(retval)
        self.assertTrue(retval == result, msg=msg)

    def _insertRecord(self, list_p, info, dir, result=Return.NORMAL):
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
        insertRecord = self._lib.DLL_InsertRecord
        insertRecord.argtypes = (POINTER(List), POINTER(Info), c_int)
        retval = insertRecord(list_p, byref(info), dir)

        msg = "Return.%s: %s" % Return.getMessage(retval)
        self.assertTrue(retval == result, msg=msg)

    def _swapRecord(self, list_p, dir, result=Return.NORMAL):
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
        swapRecord = self._lib.DLL_SwapRecord
        swapRecord.argtypes = (POINTER(List), c_int)
        retval = swapRecord(list_p, dir)

        msg = "Return.%s: %s" % Return.getMessage(retval)
        self.assertTrue(retval == result, msg=msg)

    def _updateCurrentRecord(self, list_p, record, result=Return.NORMAL):
        """
        DLL_Return DLL_UpdateCurrentRecord(List *list, Info *record);

        Arguments: list          -- Pointer to type List
                   record        -- Pointer to an Info structure in list
        Returns  : DLL_NORMAL    -- Record updated
                   DLL_NULL_LIST -- Empty list
        """
        updateCurrentRecord = self._lib.DLL_UpdateCurrentRecord
        updateCurrentRecord.argtypes = (POINTER(List), POINTER(Info),)
        retval = updateCurrentRecord(list_p, byref(record))

        msg = "Return.%s: %s" % Return.getMessage(retval)
        self.assertTrue(retval == result, msg=msg)

    def _deleteCurrentRecord(self, list_p, result=Return.NORMAL):
        """
        DLL_Return DLL_DeleteCurrentRecord(List *list);

        Arguments: list          -- Pointer to type List
        Returns  : DLL_NORMAL    -- Record deleted
                   DLL_NULL_LIST -- List is empty
        """
        deleteCurrentRecord = self._lib.DLL_DeleteCurrentRecord
        deleteCurrentRecord.argtypes = (POINTER(List),)
        retval = deleteCurrentRecord(list_p)

        msg = "Return.%s: %s" % Return.getMessage(retval)
        self.assertTrue(retval == result, msg=msg)

    def _deleteEntireList(self, list_p, result=Return.NORMAL):
        """
        DLL_Return DLL_DeleteEntireList(List *list);

        Arguments: list          -- Pointer to type List
        Returns  : DLL_NORMAL    -- List deleted
                   DLL_NULL_LIST -- List is empty
        """
        deleteEntireList = self._lib.DLL_DeleteEntireList
        deleteEntireList.argtypes = (POINTER(List),)
        retval = deleteEntireList(list_p)

        msg = "Return.%s: %s" % Return.getMessage(retval)
        self.assertTrue(retval == result, msg=msg)

    def _findRecord(self, list_p, record, match, pFun=None,
                    result=Return.NORMAL):
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
        findRecord = self._lib.DLL_FindRecord
        findRecord.argtypes = (POINTER(List), POINTER(Info), POINTER(Info),
                               c_void_p,)
        retval = findRecord(list_p, byref(record), byref(match), pFun)

        msg = "Return.%s: %s" % Return.getMessage(retval)
        self.assertTrue(retval == result, msg=msg)

        msg = "record.value: %s, match.value: %s" % (record.value, match.value)
        self.assertTrue(record.value == match.value or
                        result == Return.NOT_FOUND, msg=msg)

    def _findNthRecord(self, list_p, record, skip, test="",
                       result=Return.NORMAL):
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
        findNthRecord = self._lib.DLL_FindNthRecord
        findNthRecord.argtypes = (POINTER(List), POINTER(Info), c_ulong,)
        retval = findNthRecord(list_p, record, skip)

        msg = "Return.%s: %s" % Return.getMessage(retval)
        self.assertTrue(retval == result, msg=msg)

        #print "record.value: %s, test: %s" % (record.value, test)
        msg = "record.value: %s, test: %s" % (record.value, test)
        self.assertTrue(record.value == test or
                        result == Return.NOT_FOUND, msg=msg)

    def _getCurrentRecord(self, list_p, record, test="", result=Return.NORMAL):
        """
        DLL_Return DLL_GetCurrentRecord(List *list, Info *record);

        Arguments: list          -- Pointer to type List
                   record        -- Pointer to an Info structure
        Returns  : DLL_NORMAL    -- Record returned
                   DLL_NULL_LIST -- List is empty
        """
        getCurrentRecord = self._lib.DLL_GetCurrentRecord
        getCurrentRecord.argtypes = (POINTER(List), POINTER(Info),)
        retval = getCurrentRecord(list_p, byref(record))

        msg = "Return.%s: %s" % Return.getMessage(retval)
        self.assertTrue(retval == result, msg=msg)

        msg = "record.value: %s, test: %s" % (record.value, test)
        self.assertTrue(test == record.value, msg=msg)

    def _getPriorRecord(self, list_p, record, test="", result=Return.NORMAL):
        """
        DLL_Return DLL_GetPriorRecord(List *list, Info *record);

        Arguments: list          -- Pointer to type List
                   record        -- Pointer to an Info structure
        Returns  : DLL_NORMAL    -- Record returned
                   DLL_NULL_LIST -- List is empty
                   DLL_NOT_FOUND -- Beginning of list
        """
        getPriorRecord = self._lib.DLL_GetPriorRecord
        getPriorRecord.argtypes = (POINTER(List), POINTER(Info),)
        retval = getPriorRecord(list_p, byref(record))

        msg = "Return.%s: %s" % Return.getMessage(retval)
        self.assertTrue(retval == result, msg=msg)

        msg = "record.value: %s, test: %s" % (record.value, test)
        self.assertTrue(test == record.value, msg=msg)

    def _getNextRecord(self, list_p, record, test="", result=Return.NORMAL):
        """
        DLL_Return DLL_GetNextRecord(List *list, Info *record);

        Arguments: list          -- Pointer to type List
                   record        -- Pointer to an Info structure
        Returns  : DLL_NORMAL    -- Record returned
                   DLL_NULL_LIST -- List is empty
                   DLL_NOT_FOUND -- End of list
        """
        getNextRecord = self._lib.DLL_GetNextRecord
        getNextRecord.argtypes = (POINTER(List), POINTER(Info),)
        retval = getNextRecord(list_p, byref(record))

        msg = "Return.%s: %s" % Return.getMessage(retval)
        self.assertTrue(retval == result, msg=msg)

        msg = "record.value: %s, test: %s" % (record.value, test)
        self.assertTrue(test == record.value, msg=msg)

    def _saveList(self, list_p, path, result=Return.NORMAL):
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
        saveList = self._lib.DLL_SaveList
        saveList.argtypes = (POINTER(List), c_char_p,)
        retval = saveList(list_p, c_char_p(path))

        msg = "Return.%s: %s" % Return.getMessage(retval)
        self.assertTrue(retval == result, msg=msg)

    def _loadList(self, list_p, path, pFun=None, result=Return.NORMAL):
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
        loadList = self._lib.DLL_LoadList
        loadList.argtypes = (POINTER(List), c_char_p, c_void_p,)
        retval = loadList(list_p, c_char_p(path), pFun)

        msg = "Return.%s: %s" % Return.getMessage(retval)
        self.assertTrue(retval == result, msg=msg)

    def _cmpFunction(self):
        # Create a prototype function for the compare function.
        #cmpField(c_char_p("abcde"), c_char_p("bcdef"))
        cmpPrototype = CFUNCTYPE(c_int, c_char_p, c_char_p)
        return cmpPrototype(cmp)
