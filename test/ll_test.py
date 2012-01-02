#!/usr/bin/env python
#
# Test the Linklist API.
#
# Note: This unit test will only operate correctly on a UNIX/Linux system.
#
# $Author$
# $Date$
# $Revision$
#

import os, sys
import unittest
from ctypes import Structure, sizeof, c_char

path = os.path.join(os.path.split(os.getcwd())[0], "src")
sys.path.insert(0, path)
#print sys.path

from dlinklist import *
from dlinklist.linklist import *


class Info(Structure):
    _fields_ = (
        ('value', c_char *50),
        )


class TestLibDll(unittest.TestCase, DLinklist):

    def __init__(self, name):
        super(TestLibDll, self).__init__(name)
        DLinklist.__init__(self, disableLogging=True)
        self._list_p = None

    def setUp(self):
        # Initialize the list.
        self._list_p = self._initList(sizeof(Info))
        ## print "Address of list_p: %s" % hex(cast(self._list_p, c_void_p).value)

    def tearDown(self):
        # Destroy list.
        self._destroyList(self._list_p)

    def test_sizeofList(self):
        pSizeof = sizeof(List)
        cSizeof = self._lib._getListSize()
        msg = "Python sizeof(List): %s, C sizeof(List): %s" % (pSizeof, cSizeof)
        self.assertTrue(pSizeof == cSizeof, msg=msg)

    def test_DDL_Version(self):
        """
        Ver: 1.3.0  Dec 24 2011
        -------------------------------
        Developed by: Carl J. Nobile
        Contributions: Charlie Buckheit
                       Graham Inchley
                       Wai-Sun Chia
                       Mark M. Feenstra
                       Lianqi Qiu
        """
        devBy = " Developed by: Carl J. Nobile"
        version = string_at(self._lib.DLL_Version())

        try:
            self.assertIn(devBy, version)  # Python version => 2.7
        except:
            self.assertTrue(devBy in version)

    def test_DLL_IsListEmpty(self):
        # Check that the list is empty.
        self._isListEmpty(self._list_p, test=True)

    def test_DLL_IsListFull(self):
        # Check that the list is not full.
        self._isListFull(self._list_p, test=False)

    def test_DLL_GetNumberOfRecords(self):
        # Test empty list
        self._getNumberOfRecords(self._list_p, test=0)
        # Test list with one record
        value = "This is a test."
        self._addRecord(self._list_p, Info(value))
        self._getNumberOfRecords(self._list_p, test=1)

    def test_DLL_SetSearchModes(self):
        # Test the defaults
        self._setSearchModes(self._list_p, SrchOrigin.ORIGIN_DEFAULT,
                             SrchDir.DIRECTION_DEFAULT)
        # Test invalid SrchOrigin type
        self._setSearchModes(self._list_p, 10, SrchDir.DIRECTION_DEFAULT,
                             result=Return.NOT_MODIFIED)
        # Test invalid SrchDir type
        self._setSearchModes(self._list_p, SrchOrigin.ORIGIN_DEFAULT, 10,
                             result=Return.NOT_MODIFIED)

    def test_DLL_GetSearchModes(self):
        # Test the defaults
        searchModes = SearchModes()
        self._getSearchModes(self._list_p, searchModes)
        # Test SrchOrigin.TAIL and SrchDir.UP
        self._setSearchModes(self._list_p, SrchOrigin.TAIL, SrchDir.UP)
        self._getSearchModes(self._list_p, searchModes,
                             test=(SrchOrigin.TAIL, SrchDir.UP))

    def test_DLL_GetCurrentIndex(self):
        # Test no records
        self._getCurrentIndex(self._list_p)
        # Test one record
        value = "This is a test."
        self._addRecord(self._list_p, Info(value))
        self._getCurrentIndex(self._list_p, test=1)

    def test_DLL_CurrentPointerToHead(self):
        # Test no records
        self._currentPointerToHead(self._list_p, result=Return.NULL_LIST)
        # Test with two records
        value = "This is test record one."
        self._addRecord(self._list_p, Info(value))
        value = "This is test record two."
        self._addRecord(self._list_p, Info(value))
        self._getCurrentIndex(self._list_p, test=2)
        self._currentPointerToHead(self._list_p)
        self._getCurrentIndex(self._list_p, test=1)

    def test_DLL_CurrentPointerToTail(self):
        # Test no records
        self._currentPointerToTail(self._list_p, result=Return.NULL_LIST)
        # Test with two records
        value = "This is test record one."
        self._addRecord(self._list_p, Info(value))
        value = "This is test record two."
        self._addRecord(self._list_p, Info(value))
        self._currentPointerToHead(self._list_p)
        self._getCurrentIndex(self._list_p, test=1)
        self._currentPointerToTail(self._list_p)
        self._getCurrentIndex(self._list_p, test=2)

    def test_DLL_IncrementCurrentPointer(self):
        # Test no records
        self._incrementCurrentPointer(self._list_p, result=Return.NULL_LIST)
        # Test with two records
        value = "This is test record one."
        self._addRecord(self._list_p, Info(value))
        value = "This is test record two."
        self._addRecord(self._list_p, Info(value))
        self._currentPointerToHead(self._list_p)
        self._incrementCurrentPointer(self._list_p)
        self._getCurrentIndex(self._list_p, test=2)
        # Test past end
        self._incrementCurrentPointer(self._list_p, result=Return.NOT_FOUND)

    def test_DLL_DecrementCurrentPointer(self):
        # Test no records
        self._decrementCurrentPointer(self._list_p, result=Return.NULL_LIST)
        # Test with two records
        value = "This is test record one."
        self._addRecord(self._list_p, Info(value))
        value = "This is test record two."
        self._addRecord(self._list_p, Info(value))
        self._decrementCurrentPointer(self._list_p)
        self._getCurrentIndex(self._list_p, test=1)
        # Test past beginning
        self._decrementCurrentPointer(self._list_p, result=Return.NOT_FOUND)

    def test_DLL_Store_RestoreCurrentPointer(self):
        # Test no records
        self._storeCurrentPointer(self._list_p, result=Return.NOT_FOUND)
        self._restoreCurrentPointer(self._list_p, result=Return.NOT_FOUND)
        # Test with two records
        value = "This is test record one."
        self._addRecord(self._list_p, Info(value))
        value = "This is test record two."
        self._addRecord(self._list_p, Info(value))
        self._storeCurrentPointer(self._list_p)
        self._decrementCurrentPointer(self._list_p)
        self._getCurrentIndex(self._list_p, test=1)
        self._restoreCurrentPointer(self._list_p)
        self._getCurrentIndex(self._list_p, test=2)

    def test_DLL_AddRecord(self):
        # Test non-sorted addRecord.
        value = "This is a test."
        self._addRecord(self._list_p, Info(value))
        self._getCurrentIndex(self._list_p, test=1)
        self._getNumberOfRecords(self._list_p, test=1)
        self._deleteEntireList(self._list_p)
        self._getCurrentIndex(self._list_p, test=0)
        self._getNumberOfRecords(self._list_p, test=0)
        # Test with three records
        values = []
        values.append("ZZZZ - This is test record one.")
        values.append("AAAA - This is test record two.")
        values.append("NNNN - This is test record three.")

        for value in values:
            self._addRecord(self._list_p, Info(value), self._cmpFunction())

        # This next test will fail in version 1.2.1 and below.
        self._getCurrentIndex(self._list_p, test=2)
        values.sort()
        #print values
        self._currentPointerToHead(self._list_p)
        self._getCurrentIndex(self._list_p, test=1)
        size = len(values)

        for idx in range(size):
            self._getCurrentRecord(self._list_p, Info(), test=values[idx])
            idx < (size-1) and self._incrementCurrentPointer(self._list_p)

        self.assertTrue(idx == (size-1))

    def test_DLL_InsertRecord(self):
        values = []
        values.append("ZZZZ - This is test record one.")
        values.append("AAAA - This is test record two.")
        values.append("NNNN - This is test record three.")
        record = Info(values[0])
        self._insertRecord(self._list_p, record, InsertDir.ABOVE)
        self._getNumberOfRecords(self._list_p, test=1)
        record = Info(values[1])
        self._insertRecord(self._list_p, record, InsertDir.ABOVE)
        self._getNumberOfRecords(self._list_p, test=2)
        record = Info(values[2])
        self._insertRecord(self._list_p, record, InsertDir.BELOW)
        self._getNumberOfRecords(self._list_p, test=3)
        self._currentPointerToHead(self._list_p)
        record = Info()
        values.sort()
        size = len(values)

        for idx in range(size):
            self._getCurrentRecord(self._list_p, record, test=values[idx])
            #print record.value
            idx < (size-1) and self._incrementCurrentPointer(self._list_p)

        self.assertTrue(idx == (size-1))

    def test_DLL_SwapRecord(self):
        # Test no records
        self._swapRecord(self._list_p, InsertDir.ABOVE, result=Return.NULL_LIST)
        # Test invalid direction
        values = []
        values.append("ZZZZ - This is test record one.")
        values.append("AAAA - This is test record two.")
        values.append("NNNN - This is test record three.")

        for value in values:
            self._addRecord(self._list_p, Info(value))

        self._swapRecord(self._list_p, 10, result=Return.NOT_MODIFIED)
        self._getNumberOfRecords(self._list_p, test=3)
        # Test no record after tail
        self._getCurrentIndex(self._list_p, test=3)
        self._swapRecord(self._list_p, InsertDir.BELOW, result=Return.NOT_FOUND)
        # Test that the three records are in the correct order.
        self._getCurrentIndex(self._list_p, test=3)
        self._decrementCurrentPointer(self._list_p)
        self._swapRecord(self._list_p, InsertDir.ABOVE)
        self._getCurrentIndex(self._list_p, test=1)
        self._incrementCurrentPointer(self._list_p)
        self._swapRecord(self._list_p, InsertDir.BELOW)
        # Test no record before head
        self._currentPointerToHead(self._list_p)
        self._swapRecord(self._list_p, InsertDir.ABOVE, result=Return.NOT_FOUND)
        # Continue with correct order test.
        record = Info()
        values.sort()
        size = len(values)

        for idx in range(size):
            self._getCurrentRecord(self._list_p, record, test=values[idx])
            #print record.value
            idx < (size-1) and self._incrementCurrentPointer(self._list_p)

        self.assertTrue(idx == (size-1))

    def test_DLL_UpdateCurrentRecord(self):
        # Test no records
        value = "This is a text."
        self._updateCurrentRecord(self._list_p, Info(value),
                                  result=Return.NULL_LIST)
        # Test that the record got updated
        self._addRecord(self._list_p, Info(value))
        self._getCurrentRecord(self._list_p, Info(), test=value)
        value = "This is another text."
        self._updateCurrentRecord(self._list_p, Info(value))
        self._getCurrentRecord(self._list_p, Info(), test=value)

    def test_DLL_DeleteCurrentRecord(self):
        # Test no records
        self._deleteCurrentRecord(self._list_p, result=Return.NULL_LIST)
        # Test that the record got deleted
        value = "This is a text."
        self._addRecord(self._list_p, Info(value))
        self._getCurrentIndex(self._list_p, test=1)
        self._deleteCurrentRecord(self._list_p)
        self._isListEmpty(self._list_p, test=True)

    def test_DLL_DeleteEntireList(self):
        # Test no records
        self._deleteEntireList(self._list_p, result=Return.NULL_LIST)
        # Test thst the list gets deleted
        values = []
        values.append("ZZZZ - This is test record one.")
        values.append("AAAA - This is test record two.")
        values.append("NNNN - This is test record three.")

        for value in values:
            self._addRecord(self._list_p, Info(value))

        self._getNumberOfRecords(self._list_p, test=3)
        self._deleteEntireList(self._list_p)
        self._isListEmpty(self._list_p, test=True)

    def test_DLL_FindRecord(self):
        # Test for null function pointer
        self._findRecord(self._list_p, Info(), Info(), None,
                         result=Return.NULL_FUNCTION)
        # Test no records
        self._findRecord(self._list_p, Info(), Info(), self._cmpFunction(),
                         result=Return.NULL_LIST)
        # Test that record if found
        values = []
        values.append("ZZZZ - This is test record one.")
        values.append("AAAA - This is test record two.")
        values.append("NNNN - This is test record three.")

        for value in values:
            self._addRecord(self._list_p, Info(value))

        self._getNumberOfRecords(self._list_p, test=3)
        record = Info()
        self._findRecord(self._list_p, record, Info(values[1]),
                         self._cmpFunction())
        # Test record not found
        self._findRecord(self._list_p, record, Info("Record not found."),
                         self._cmpFunction(), result=Return.NOT_FOUND)

    def test_DLL_FindNthRecord(self):
        # Test no records
        self._findNthRecord(self._list_p, Info(), 1, result=Return.NULL_LIST)
        # Test for the Nth record, step = 1 then 5
        # (Uses defaults in the list struct, SrchOrigin.HEAD and SrchDir.DOWN)
        values = []
        values.append("ZZZZ - This is test record one.")
        values.append("AAAA - This is test record two.")
        values.append("NNNN - This is test record three.")
        values.append("YYYY - This is test record four.")
        values.append("BBBB - This is test record five.")
        values.append("MMMM - This is test record six.")

        for value in values:
            self._addRecord(self._list_p, Info(value))

        self._getNumberOfRecords(self._list_p, test=6)
        self._getCurrentIndex(self._list_p, test=6)
        self._findNthRecord(self._list_p, Info(), 1, test=values[1])
        self._getCurrentIndex(self._list_p, test=2)
        self._findNthRecord(self._list_p, Info(), 5, test=values[5])
        self._getCurrentIndex(self._list_p, test=6)
        # Test invalid skip value with SrchOrigin.HEAD and SrchDir.DOWN
        self._findNthRecord(self._list_p, Info(), 0, test=values[1],
                            result=Return.NOT_FOUND)
        self._findNthRecord(self._list_p, Info(), 6, test=values[1],
                            result=Return.NOT_FOUND)
        # Test change search mode to SrchOrigin.TAIL and SrchDir.UP
        self._setSearchModes(self._list_p, SrchOrigin.TAIL, SrchDir.UP)
        self._findNthRecord(self._list_p, Info(), 1, test=values[4])
        self._getCurrentIndex(self._list_p, test=5)
        self._findNthRecord(self._list_p, Info(), 5, test=values[0])
        self._getCurrentIndex(self._list_p, test=1)
        # Test invalid skip value with SrchOrigin.TAIL and SrchDir.UP
        self._findNthRecord(self._list_p, Info(), 6, test=values[5],
                            result=Return.NOT_FOUND)
        # Test change search mode to SrchOrigin.CURRENT and SrchDir.DOWN
        self._setSearchModes(self._list_p, SrchOrigin.CURRENT, SrchDir.DOWN)
        # TODO -- enhance the increment and decrement current pointer to
        # to increment or decrement a number of records.
        self._incrementCurrentPointer(self._list_p)
        self._incrementCurrentPointer(self._list_p)
        self._findNthRecord(self._list_p, Info(), 1, test=values[3])
        self._getCurrentIndex(self._list_p, test=4)
        # Test invalid skip value with SrchOrigin.CURRENT and SrchDir.DOWN
        self._findNthRecord(self._list_p, Info(), 3, test=values[5],
                            result=Return.NOT_FOUND)
        self._getCurrentIndex(self._list_p, test=4)
        # Test change search mode to SrchOrigin.CURRENT and SrchDir.UP
        self._setSearchModes(self._list_p, SrchOrigin.CURRENT, SrchDir.UP)
        self._findNthRecord(self._list_p, Info(), 1, test=values[2])
        self._getCurrentIndex(self._list_p, test=3)
        # Test invalid skip value with SrchOrigin.CURRENT and SrchDir.UP
        self._findNthRecord(self._list_p, Info(), 3, test=values[0],
                            result=Return.NOT_FOUND)
        self._getCurrentIndex(self._list_p, test=3)

    def test_DLL_GetCurrentRecord(self):
        # Test no records
        self._getCurrentRecord(self._list_p, Info(), result=Return.NULL_LIST)
        # Test for curent record
        value = "This is test record."
        self._addRecord(self._list_p, Info(value))
        self._getCurrentRecord(self._list_p, Info(), test=value)
        self._getCurrentIndex(self._list_p, test=1)

    def test_DLL_GetPriorRecord(self):
        # Test no records
        self._getPriorRecord(self._list_p, Info(), result=Return.NULL_LIST)
        # Test for curent record
        values = []
        values.append("ZZZZ - This is test record one.")
        values.append("AAAA - This is test record two.")

        for value in values:
            self._addRecord(self._list_p, Info(value))

        self._currentPointerToTail(self._list_p)
        self._getPriorRecord(self._list_p, Info(), test=values[0])
        self._getCurrentIndex(self._list_p, test=1)

    def test_DLL_GetNextRecord(self):
        # Test no records
        self._getNextRecord(self._list_p, Info(), result=Return.NULL_LIST)
        # Test for curent record
        values = []
        values.append("ZZZZ - This is test record one.")
        values.append("AAAA - This is test record two.")

        for value in values:
            self._addRecord(self._list_p, Info(value))

        self._currentPointerToHead(self._list_p)
        self._getNextRecord(self._list_p, Info(), test=values[1])
        self._getCurrentIndex(self._list_p, test=2)

    def test_DLL_Save_LoadList(self):
        filePath = "unittest.data"
        # Test no records
        self._saveList(self._list_p, filePath, result=Return.NULL_LIST)
        # Test saving list to dick
        values = []
        values.append("ZZZZ - This is test record one.")
        values.append("AAAA - This is test record two.")
        values.append("NNNN - This is test record three.")
        values.append("YYYY - This is test record four.")
        values.append("BBBB - This is test record five.")
        values.append("MMMM - This is test record six.")

        for value in values:
            self._addRecord(self._list_p, Info(value))

        self._getNumberOfRecords(self._list_p, test=6)
        self._saveList(self._list_p, filePath)
        # Test already has data in list.
        self._saveList(self._list_p, filePath, result=Return.NOT_MODIFIED)
        # Test load list.
        self._loadList(self._list_p, filePath, self._cmpFunction())
        # The current index is an arbitrary number depending on the sort
        # algorithm used. This next test will fail in version 1.2.1 and below.
        self._getCurrentIndex(self._list_p, test=3)
        self._currentPointerToHead(self._list_p)
        self._getCurrentIndex(self._list_p, test=1)
        # Test open error.
        self._loadList(self._list_p, "", self._cmpFunction(),
                       result=Return.OPEN_ERROR)
        self._getCurrentIndex(self._list_p, test=1)
        os.remove(filePath)

    #
    # Methods to interface into ctypes.
    #
    def _initList(self, infoSize):
        """
        List *DLL_CreateList(List **list);

        Arguments: list -- Pointer to a pointer to a name of a structure to
                           create.
        Returns  : Pointer to created structure
                   NULL if unsuccessful


        DLL_Return DLL_InitializeList(List *list, size_t infosize);

        Arguments: list          -- Pointer to type List
                   infosize      -- Size of user Info
        Returns  : DLL_NORMAL    -- Initialization was done successfully
                   DLL_ZERO_INFO -- sizeof(Info) is zero
                   DLL_NULL_LIST -- Info is NULL
        """
        try:
            list_p = self.create(infoSize)
        except APIException, e:
            self.fail(e)
        except FunctionException, e:
            self.fail(e)

        msg = "DLL_CreateList failed, list_p: %s."
        self.assertTrue(list_p not in (0, None),
                        msg=msg % hex(cast(list_p, c_void_p).value))

        return list_p

    def _destroyList(self, list_p):
        """
        void DLL_DestroyList(List **list);

        Arguments: list -- Pointer to a pointer to a name of a structure to
                           destroy.
        Returns  : void
        """
        try:
            self.destroy(list_p)
        except APIException, e:
            self.fail(e)

    def _isListEmpty(self, list_p, test=True):
        """
        DLL_Boolean DLL_IsListEmpty(List *list);

        Arguments: list          -- Pointer to type List
        Returns  : DLL_TRUE  -- List is empty
                   DLL_FALSE -- List has items in it
        """
        try:
            retval = self.isListEmpty(list_p)
        except APIException, e:
            self.fail(e)

        msg = "retval: %s, test: %s"
        self.assertTrue(retval == test, msg=msg % (retval, test))

    def _isListFull(self, list_p, test=True):
        """
        DLL_Boolean DLL_IsListFull(List *list);

        Arguments: list      -- Pointer to type List
        Returns  : DLL_TRUE  -- List is full (memory dependent)
                   DLL_FALSE -- List is empty or partially full
        """
        try:
            retval = self.isListFull(list_p)
        except APIException, e:
            self.fail(e)

        msg = "retval: %s, test: %s"
        self.assertTrue(retval == test, msg=msg % (retval, test))

    def _getNumberOfRecords(self, list_p, test=0):
        """
        unsigned long DLL_GetNumberOfRecords(List *list);

        Arguments: list -- Pointer to type List
        Returns  : Number of records in list
        """
        try:
            retval = self.getNumberOfRecords(list_p)
        except APIException, e:
            self.fail(e)

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
        try:
            retval = self.setSearchModes(list_p, origin, dir)
        except APIException, e:
            self.fail(e)
        except FunctionException, e:
            msg = "Return.%s: %s" % Return.getMessage(e.getRetval())
            self.assertTrue(e.getRetval() == result, msg=msg)

    def _getSearchModes(self, list_p, sm, test=(SrchOrigin.HEAD, SrchDir.DOWN)):
        """
        DLL_SearchModes DLL_GetSearchModes(List *list, DLL_SearchModes *ssp);

        Arguments: list -- Pointer to type List
                   ssp  -- Save structure pointer
        Returns  : Pointer to type DLL_SearchModes
        """
        try:
            modes = self.getSearchModes(list_p, sm)
        except APIException, e:
            self.fail(e)
 
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
        try:
            retval = self.getCurrentIndex(list_p)
        except APIException, e:
            self.fail(e)

        msg = "retval: %s, test: %s"
        self.assertTrue(retval == test, msg=msg % (retval, test))

    def _currentPointerToHead(self, list_p, result=Return.NORMAL):
        """
        DLL_Return DLL_CurrentPointerToHead(List *list);

        Arguments: list          -- Pointer to type List
        Returns  : DLL_NORMAL    -- Record found
                   DLL_NULL_LIST -- Empty list
        """
        try:
            retval = self.currentPointerToHead(list_p)
        except APIException, e:
            self.fail(e)
        except FunctionException, e:
            msg = "Return.%s: %s" % Return.getMessage(e.getRetval())
            self.assertTrue(e.getRetval() == result, msg=msg)

    def _currentPointerToTail(self, list_p, result=Return.NORMAL):
        """
        DLL_Return DLL_CurrentPointerToTail(List *list);

        Arguments: list          -- Pointer to type List
        Returns  : DLL_NORMAL    -- Record found
                   DLL_NULL_LIST -- Empty list
        """
        try:
            retval = self.currentPointerToTail(list_p)
        except APIException, e:
            self.fail(e)
        except FunctionException, e:
            msg = "Return.%s: %s" % Return.getMessage(e.getRetval())
            self.assertTrue(e.getRetval() == result, msg=msg)

    def _incrementCurrentPointer(self, list_p, result=Return.NORMAL):
        """
        DLL_Return DLL_IncrementCurrentPointer(List *list);

        Arguments: list          -- Pointer to type List
        Returns  : DLL_NORMAL    -- Record found
                   DLL_NULL_LIST -- Empty list
                   DLL_NOT_FOUND -- Record not found
        """
        try:
            retval = self.incrementCurrentPointer(list_p)
        except APIException, e:
            self.fail(e)
        except FunctionException, e:
            msg = "Return.%s: %s" % Return.getMessage(e.getRetval())
            self.assertTrue(e.getRetval() == result, msg=msg)

    def _decrementCurrentPointer(self, list_p, result=Return.NORMAL):
        """
        DLL_Return DLL_DecrementCurrentPointer(List *list);

        Arguments: list          -- Pointer to type List
        Returns  : DLL_NORMAL    -- Record found
                   DLL_NULL_LIST -- Empty list
                   DLL_NOT_FOUND -- Record not found
        """
        try:
            retval = self.decrementCurrentPointer(list_p)
        except APIException, e:
            self.fail(e)
        except FunctionException, e:
            msg = "Return.%s: %s" % Return.getMessage(e.getRetval())
            self.assertTrue(e.getRetval() == result, msg=msg)

    def _storeCurrentPointer(self, list_p, result=Return.NORMAL):
        """
        DLL_Return DLL_StoreCurrentPointer(List *list);

        Arguments: list          -- Pointer to type List
        Returns  : DLL_NORMAL    -- Record found
                   DLL_NOT_FOUND -- Record not found
        """
        try:
            retval = self.storeCurrentPointer(list_p)
        except APIException, e:
            self.fail(e)
        except FunctionException, e:
            msg = "Return.%s: %s" % Return.getMessage(e.getRetval())
            self.assertTrue(e.getRetval() == result, msg=msg)

    def _restoreCurrentPointer(self, list_p, result=Return.NORMAL):
        """
        DLL_Return DLL_restoreCurrentPointer(List *list);

        Arguments: list          -- Pointer to type List
        Returns  : DLL_NORMAL    -- Record found
                   DLL_NOT_FOUND -- Record not found
        """
        try:
            retval = self.restoreCurrentPointer(list_p)
        except APIException, e:
            self.fail(e)
        except FunctionException, e:
            msg = "Return.%s: %s" % Return.getMessage(e.getRetval())
            self.assertTrue(e.getRetval() == result, msg=msg)

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
        try:
            retval = self.addRecord(list_p, info, pFun=pFun)
        except APIException, e:
            self.fail(e)
        except FunctionException, e:
            msg = "Return.%s: %s" % Return.getMessage(e.getRetval())
            self.assertTrue(e.getRetval() == result, msg=msg)

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
        try:
            retval = self.insertRecord(list_p, info, dir)
        except APIException, e:
            self.fail(e)
        except FunctionException, e:
            msg = "Return.%s: %s" % Return.getMessage(e.getRetval())
            self.assertTrue(e.getRetval() == result, msg=msg)

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
        try:
            retval = self.swapRecord(list_p, dir)
        except APIException, e:
            self.fail(e)
        except FunctionException, e:
            msg = "Return.%s: %s" % Return.getMessage(e.getRetval())
            self.assertTrue(e.getRetval() == result, msg=msg)

    def _updateCurrentRecord(self, list_p, record, result=Return.NORMAL):
        """
        DLL_Return DLL_UpdateCurrentRecord(List *list, Info *record);

        Arguments: list          -- Pointer to type List
                   record        -- Pointer to an Info structure in list
        Returns  : DLL_NORMAL    -- Record updated
                   DLL_NULL_LIST -- Empty list
        """
        try:
            retval = self.updateCurrentRecord(list_p, record)
        except APIException, e:
            self.fail(e)
        except FunctionException, e:
            msg = "Return.%s: %s" % Return.getMessage(e.getRetval())
            self.assertTrue(e.getRetval() == result, msg=msg)

    def _deleteCurrentRecord(self, list_p, result=Return.NORMAL):
        """
        DLL_Return DLL_DeleteCurrentRecord(List *list);

        Arguments: list          -- Pointer to type List
        Returns  : DLL_NORMAL    -- Record deleted
                   DLL_NULL_LIST -- List is empty
        """
        try:
            retval = self.deleteCurrentRecord(list_p)
        except APIException, e:
            self.fail(e)
        except FunctionException, e:
            msg = "Return.%s: %s" % Return.getMessage(e.getRetval())
            self.assertTrue(e.getRetval() == result, msg=msg)

    def _deleteEntireList(self, list_p, result=Return.NORMAL):
        """
        DLL_Return DLL_DeleteEntireList(List *list);

        Arguments: list          -- Pointer to type List
        Returns  : DLL_NORMAL    -- List deleted
                   DLL_NULL_LIST -- List is empty
        """
        try:
            retval = self.deleteAllNodes(list_p)
        except APIException, e:
            self.fail(e)
        except FunctionException, e:
            msg = "Return.%s: %s" % Return.getMessage(e.getRetval())
            self.assertTrue(e.getRetval() == result, msg=msg)

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
        try:
            retval = self.findRecord(list_p, record, match, pFun=pFun)
        except APIException, e:
            self.fail(e)
        except FunctionException, e:
            msg = "Return.%s: %s" % Return.getMessage(e.getRetval())
            self.assertTrue(e.getRetval() == result, msg=msg)

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
        try:
            retval = self.findNthRecord(list_p, record, skip)
        except APIException, e:
            self.fail(e)
        except FunctionException, e:
            msg = "Return.%s: %s" % Return.getMessage(e.getRetval())
            self.assertTrue(e.getRetval() == result, msg=msg)

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
        try:
            retval = self.getCurrentRecord(list_p, record)
        except APIException, e:
            self.fail(e)
        except FunctionException, e:
            msg = "Return.%s: %s" % Return.getMessage(e.getRetval())
            self.assertTrue(e.getRetval() == result, msg=msg)

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
        try:
            retval = self.getPriorRecord(list_p, record)
        except APIException, e:
            self.fail(e)
        except FunctionException, e:
            msg = "Return.%s: %s" % Return.getMessage(e.getRetval())
            self.assertTrue(e.getRetval() == result, msg=msg)

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
        try:
            retval = self.getNextRecord(list_p, record)
        except APIException, e:
            self.fail(e)
        except FunctionException, e:
            msg = "Return.%s: %s" % Return.getMessage(e.getRetval())
            self.assertTrue(e.getRetval() == result, msg=msg)

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
        try:
            retval = self.saveList(list_p, path)
        except APIException, e:
            self.fail(e)
        except FunctionException, e:
            msg = "Return.%s: %s" % Return.getMessage(e.getRetval())
            self.assertTrue(e.getRetval() == result, msg=msg)

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
        try:
            retval = self.loadList(list_p, path, pFun=pFun)
        except APIException, e:
            self.fail(e)
        except FunctionException, e:
            msg = "Return.%s: %s" % Return.getMessage(e.getRetval())
            self.assertTrue(e.getRetval() == result, msg=msg)

    def _cmpFunction(self):
        # Create a prototype function for the compare function.
        #cmpField(c_char_p("abcde"), c_char_p("bcdef"))
        cmpPrototype = CFUNCTYPE(c_int, c_char_p, c_char_p)
        return cmpPrototype(cmp)


if __name__ == '__main__':
    unittest.main()
