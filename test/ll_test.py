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
from ctypes import Structure, sizeof, string_at, cast, c_char, c_void_p

path = os.path.join(os.path.split(os.getcwd())[0], "src")
sys.path.insert(0, path)
#print sys.path

from dlinklist import APIException, FunctionException, DLinklist, Return, \
     SrchOrigin, SrchDir, InsertDir
from dlinklist.linklist import List

class Info(Structure):
    _fields_ = (
        ('value', c_char * 50),
        )


class TestLibDll(unittest.TestCase):
    """
    This class runs testunit test on all the function in my C{C} linklist
    library.
    """

    def __init__(self, name):
        """
        Initializes the C{TestLibDll} class.

          1. Call the constructor of the base class.
          2. Create an aggreget of the C{DLinklist} class.
          3. Define an object to be used for a C{ctypes} C{POINTER} object.

        @param name: The name used by the C{TestCase} class.
        @raise LibraryNotFoundException: If the C{C} library cannot be found.
        """
        super(TestLibDll, self).__init__(name)
        self._dll = DLinklist(disableLogging=True)
        self._list_p = None

    def setUp(self):
        """
        Initialize the list for each unit test.

        @return: C{None}
        """
        # Create and initialize list
        self._list_p = self._initList(sizeof(Info))
        #print "Address of list_p: %s" % hex(cast(self._list_p, c_void_p).value)

    def tearDown(self):
        """
        Destroy entire list.

        @return: C{None}
        """
        # Destroy list.
        self._destroyList()

    def test_InfoType(self):
        """
        Check that the C{Info} class is the correct type.

        @return: C{None}
        """
        msg = "Invalid Info type is not a subclass of ctypes Structure."

        try:
            self._dll.checkInfoType(Info())
        except:
            self.fail(msg)

        class BadInfo(object):
            pass

        try:
            self._dll.checkInfoType(BadInfo())
            self.fail(msg)
        except APIException:
            pass

    def test_sizeofList(self):
        """
        Test that the C{Python} C{List} object is the same size as the C{C}
        C{List} structure.

        @return: C{None}
        """
        pSizeof = sizeof(List)
        cSizeof = self._dll._lib._getListSize()
        msg = "Python sizeof(List): %s, C sizeof(List): %s" % (pSizeof, cSizeof)
        self.assertTrue(pSizeof == cSizeof, msg=msg)

    def test_DDL_Version(self):
        """
        Test that a string is returned.

        The C{C} function doc string::

          Ver: 1.3.0  Dec 24 2011
          -------------------------------
          Developed by: Carl J. Nobile
          Contributions: Charlie Buckheit
                         Graham Inchley
                         Wai-Sun Chia
                         Mark M. Feenstra
                         Lianqi Qiu

        @return: C{None}
        """
        devBy = " Developed by: Carl J. Nobile"
        version = string_at(self._dll.version())

        try:
            self.assertIn(devBy, version)  # Python version => 2.7
        except:
            self.assertTrue(devBy in version)

    def test_DLL_IsListEmpty(self):
        """
        Check that the list is empty.

        @return: C{None}
        """
        self._isListEmpty(test=True)

    def test_DLL_IsListFull(self):
        """
        Check that the list is not full.

        @return: C{None}
        """
        self._isListFull(test=False)

    def test_DLL_GetNumberOfRecords(self):
        """
        Check that the correct number of records are returned.

        @return: C{None}
        """
        # Test that list is empty
        self._getNumberOfRecords(test=0)
        # Test list with one record
        value = "This is a test."
        self._addRecord(Info(value))
        self._getNumberOfRecords(test=1)

    def test_DLL_SetSearchModes(self):
        """
        Check that the correct return codes are returned when setting the
        search modes.

        @return: C{None}
        """
        # Test the defaults
        self._setSearchModes(SrchOrigin.ORIGIN_DEFAULT,
                             SrchDir.DIRECTION_DEFAULT)
        # Test invalid SrchOrigin type
        self._setSearchModes(10, SrchDir.DIRECTION_DEFAULT,
                             result=Return.NOT_MODIFIED)
        # Test invalid SrchDir type
        self._setSearchModes(SrchOrigin.ORIGIN_DEFAULT, 10,
                             result=Return.NOT_MODIFIED)

    def test_DLL_GetSearchModes(self):
        """
        Check that the set search modes are returned.

        @return: C{None}
        """
        # Test the defaults
        self._getSearchModes()
        # Test SrchOrigin.TAIL and SrchDir.UP
        self._setSearchModes(SrchOrigin.TAIL, SrchDir.UP)
        self._getSearchModes(test=(SrchOrigin.TAIL, SrchDir.UP))

    def test_DLL_GetCurrentIndex(self):
        """
        Check that the current index is returned.

        @return: C{None}
        """
        # Test no records
        self._getCurrentIndex()
        # Test one record
        value = "This is a test."
        self._addRecord(Info(value))
        self._getCurrentIndex(test=1)

    def test_DLL_CurrentPointerToHead(self):
        """
        Check that the current pointer gets moved to the head of the list
        properly and that the correct return codes are returned.

        @return: C{None}
        """
        # Test no records
        self._currentPointerToHead(result=Return.NULL_LIST)
        # Test with two records
        value = "This is test record one."
        self._addRecord(Info(value))
        value = "This is test record two."
        self._addRecord(Info(value))
        self._getCurrentIndex(test=2)
        self._currentPointerToHead()
        self._getCurrentIndex(test=1)

    def test_DLL_CurrentPointerToTail(self):
        """
        Check that the current pointer gets moved to the tail of the list
        properly and that the correct return codes are returned.

        @return: C{None}
        """
        # Test no records
        self._currentPointerToTail(result=Return.NULL_LIST)
        # Test with two records
        value = "This is test record one."
        self._addRecord(Info(value))
        value = "This is test record two."
        self._addRecord(Info(value))
        self._currentPointerToHead()
        self._getCurrentIndex(test=1)
        self._currentPointerToTail()
        self._getCurrentIndex(test=2)

    def test_DLL_IncrementCurrentPointer(self):
        """
        Check that the current pointer gets incremented properly and that the
        correct return codes are returned.

        @return: C{None}
        """
        # Test no records
        self._incrementCurrentPointer(result=Return.NULL_LIST)
        # Test with two records
        value = "This is test record one."
        self._addRecord(Info(value))
        value = "This is test record two."
        self._addRecord(Info(value))
        self._currentPointerToHead()
        self._incrementCurrentPointer()
        self._getCurrentIndex(test=2)
        # Test past end
        self._incrementCurrentPointer(result=Return.NOT_FOUND)

    def test_DLL_DecrementCurrentPointer(self):
        """
        Check that the current pointer gets decremented properly and that the
        correct return codes are returned.

        @return: C{None}
        """
        # Test no records
        self._decrementCurrentPointer(result=Return.NULL_LIST)
        # Test with two records
        value = "This is test record one."
        self._addRecord(Info(value))
        value = "This is test record two."
        self._addRecord(Info(value))
        self._decrementCurrentPointer()
        self._getCurrentIndex(test=1)
        # Test past beginning
        self._decrementCurrentPointer(result=Return.NOT_FOUND)

    def test_DLL_Store_RestoreCurrentPointer(self):
        """
        Check that the store and restore of the current pointer is properly
        done and the correct return codes are returned.

        @return: C{None}
        """
        # Test no records
        self._storeCurrentPointer(result=Return.NOT_FOUND)
        self._restoreCurrentPointer(result=Return.NOT_FOUND)
        # Test with two records
        value = "This is test record one."
        self._addRecord(Info(value))
        value = "This is test record two."
        self._addRecord(Info(value))
        self._storeCurrentPointer()
        self._decrementCurrentPointer()
        self._getCurrentIndex(test=1)
        self._restoreCurrentPointer()
        self._getCurrentIndex(test=2)

    def test_DLL_AddRecord(self):
        """
        Check that records are added to the link list properly, the index
        values are correct after each add, and the correct return codes are
        returned.

        @return: C{None}
        """
        # Test non-sorted addRecord.
        value = "This is a test."
        self._addRecord(Info(value))
        self._getCurrentIndex(test=1)
        self._getNumberOfRecords(test=1)
        self._deleteEntireList()
        self._getCurrentIndex(test=0)
        self._getNumberOfRecords(test=0)
        # Test with three records
        values = []
        values.append("ZZZZ - This is test record one.")
        values.append("AAAA - This is test record two.")
        values.append("NNNN - This is test record three.")

        for value in values:
            self._addRecord(Info(value), self._dll.compare())

        # This next test will fail in version 1.2.1 and below.
        self._getCurrentIndex(test=2)
        values.sort()
        #print values
        self._currentPointerToHead()
        self._getCurrentIndex(test=1)
        size = len(values)

        for idx in range(size):
            self._getCurrentRecord(Info(), test=values[idx])
            idx < (size-1) and self._incrementCurrentPointer()

        self.assertTrue(idx == (size-1))

    def test_DLL_InsertRecord(self):
        """
        Check that inserted records are added properly based on C{InsertDir},
        the index values are correct after each insert, and the correct return
        codes are returned.

        @return: C{None}
        """
        values = []
        values.append("ZZZZ - This is test record one.")
        values.append("AAAA - This is test record two.")
        values.append("NNNN - This is test record three.")
        record = Info(values[0])
        self._insertRecord(record, InsertDir.ABOVE)
        self._getNumberOfRecords(test=1)
        record = Info(values[1])
        self._insertRecord(record, InsertDir.ABOVE)
        self._getNumberOfRecords(test=2)
        record = Info(values[2])
        self._insertRecord(record, InsertDir.BELOW)
        self._getNumberOfRecords(test=3)
        self._currentPointerToHead()
        record = Info()
        values.sort()
        size = len(values)

        for idx in range(size):
            self._getCurrentRecord(record, test=values[idx])
            #print record.value
            idx < (size-1) and self._incrementCurrentPointer()

        self.assertTrue(idx == (size-1))

    def test_DLL_SwapRecord(self):
        """
        Check that the current record is swapped correctly based on
        C{InsertDir}, the index values are correct after each swap, and the
        correct return codes are returned.

        @return: C{None}
        """
        # Test no records
        self._swapRecord(InsertDir.ABOVE, result=Return.NULL_LIST)
        # Test invalid direction
        values = []
        values.append("ZZZZ - This is test record one.")
        values.append("AAAA - This is test record two.")
        values.append("NNNN - This is test record three.")

        for value in values:
            self._addRecord(Info(value))

        self._swapRecord(10, result=Return.NOT_MODIFIED)
        self._getNumberOfRecords(test=3)
        # Test no record after tail
        self._getCurrentIndex(test=3)
        self._swapRecord(InsertDir.BELOW, result=Return.NOT_FOUND)
        # Test that the three records are in the correct order.
        self._getCurrentIndex(test=3)
        self._decrementCurrentPointer()
        self._swapRecord(InsertDir.ABOVE)
        self._getCurrentIndex(test=1)
        self._incrementCurrentPointer()
        self._swapRecord(InsertDir.BELOW)
        # Test no record before head
        self._currentPointerToHead()
        self._swapRecord(InsertDir.ABOVE, result=Return.NOT_FOUND)
        # Continue with correct order test.
        record = Info()
        values.sort()
        size = len(values)

        for idx in range(size):
            self._getCurrentRecord(record, test=values[idx])
            #print record.value
            idx < (size-1) and self._incrementCurrentPointer()

        self.assertTrue(idx == (size-1))

    def test_DLL_UpdateCurrentRecord(self):
        """
        Check that a record gets updated correctly, the index values are
        correct after each update, and the correct return codes are returned.

        @return: C{None}
        """
        # Test no records
        value = "This is a text."
        self._updateCurrentRecord(Info(value),
                                  result=Return.NULL_LIST)
        self._getCurrentIndex(test=0)
        # Test that the record got updated
        self._addRecord(Info(value))
        self._getCurrentRecord(Info(), test=value)
        self._getCurrentIndex(test=1)
        value = "This is another text."
        self._updateCurrentRecord(Info(value))
        self._getCurrentIndex(test=1)
        self._getCurrentRecord(Info(), test=value)
        self._getCurrentIndex(test=1)

    def test_DLL_DeleteCurrentRecord(self):
        """
        Check that a record gets deleted correctly, the index values are
        correct after each update, and the correct return codes are returned.

        @return: C{None}
        """
        # Test no records
        self._deleteCurrentRecord(result=Return.NULL_LIST)
        self._getCurrentIndex(test=0)
        # Test that the record got deleted
        value = "This is a text."
        self._addRecord(Info(value))
        self._getCurrentIndex(test=1)
        self._deleteCurrentRecord()
        self._isListEmpty(test=True)

    def test_DLL_DeleteEntireList(self):
        """
        Check that the entire list is deleted properly, the index values are
        correct after the delete, and the correct return codes are returned.

        @return: C{None}
        """
        # Test no records
        self._deleteEntireList(result=Return.NULL_LIST)
        # Test thst the list gets deleted
        values = []
        values.append("ZZZZ - This is test record one.")
        values.append("AAAA - This is test record two.")
        values.append("NNNN - This is test record three.")

        for value in values:
            self._addRecord(Info(value))

        self._getNumberOfRecords(test=3)
        self._deleteEntireList()
        self._isListEmpty(test=True)

    def test_DLL_FindRecord(self):
        """
        Check that records are found correctly, the index values are correct
        after each query, and the correct return codes are returned.

        @return: C{None}
        """
        # Test for null function pointer
        self._findRecord(Info(), Info(), None,
                         result=Return.NULL_FUNCTION)
        # Test no records
        self._findRecord(Info(), Info(), self._dll.compare(),
                         result=Return.NULL_LIST)
        # Test that record if found
        values = []
        values.append("ZZZZ - This is test record one.")
        values.append("AAAA - This is test record two.")
        values.append("NNNN - This is test record three.")

        for value in values:
            self._addRecord(Info(value))

        self._getNumberOfRecords(test=3)
        record = Info()
        self._findRecord(record, Info(values[1]), self._dll.compare())
        # Test record not found
        self._findRecord(record, Info("Record not found."),
                         self._dll.compare(), result=Return.NOT_FOUND)

    def test_DLL_FindNthRecord(self):
        """
        Check that records are found correctly based on the skip value, the
        index values are correct after each query, and the correct return
        codes are returned.

        @return: C{None}
        """
        # Test no records
        self._findNthRecord(Info(), 1, result=Return.NULL_LIST)
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
            self._addRecord(Info(value))

        self._getNumberOfRecords(test=6)
        self._getCurrentIndex(test=6)
        self._findNthRecord(Info(), 1, test=values[1])
        self._getCurrentIndex(test=2)
        self._findNthRecord(Info(), 5, test=values[5])
        self._getCurrentIndex(test=6)
        # Test invalid skip value with SrchOrigin.HEAD and SrchDir.DOWN
        self._findNthRecord(Info(), 0, test=values[1],
                            result=Return.NOT_FOUND)
        self._findNthRecord(Info(), 6, test=values[1],
                            result=Return.NOT_FOUND)
        # Test change search mode to SrchOrigin.TAIL and SrchDir.UP
        self._setSearchModes(SrchOrigin.TAIL, SrchDir.UP)
        self._findNthRecord(Info(), 1, test=values[4])
        self._getCurrentIndex(test=5)
        self._findNthRecord(Info(), 5, test=values[0])
        self._getCurrentIndex(test=1)
        # Test invalid skip value with SrchOrigin.TAIL and SrchDir.UP
        self._findNthRecord(Info(), 6, test=values[5],
                            result=Return.NOT_FOUND)
        # Test change search mode to SrchOrigin.CURRENT and SrchDir.DOWN
        self._setSearchModes(SrchOrigin.CURRENT, SrchDir.DOWN)
        # TODO -- enhance the increment and decrement current pointer to
        # to increment or decrement a number of records.
        self._incrementCurrentPointer()
        self._incrementCurrentPointer()
        self._findNthRecord(Info(), 1, test=values[3])
        self._getCurrentIndex(test=4)
        # Test invalid skip value with SrchOrigin.CURRENT and SrchDir.DOWN
        self._findNthRecord(Info(), 3, test=values[5],
                            result=Return.NOT_FOUND)
        self._getCurrentIndex(test=4)
        # Test change search mode to SrchOrigin.CURRENT and SrchDir.UP
        self._setSearchModes(SrchOrigin.CURRENT, SrchDir.UP)
        self._findNthRecord(Info(), 1, test=values[2])
        self._getCurrentIndex(test=3)
        # Test invalid skip value with SrchOrigin.CURRENT and SrchDir.UP
        self._findNthRecord(Info(), 3, test=values[0],
                            result=Return.NOT_FOUND)
        self._getCurrentIndex(test=3)

    def test_DLL_GetCurrentRecord(self):
        """
        Check that the current record is returned correctly, the index values
        are correct after the get, and the correct return codes are returned.

        @return: C{None}
        """
        # Test no records
        self._getCurrentRecord(Info(), result=Return.NULL_LIST)
        self._getCurrentIndex(test=0)
        # Test for curent record
        value = "This is test record."
        self._addRecord(Info(value))
        self._getCurrentRecord(Info(), test=value)
        self._getCurrentIndex(test=1)

    def test_DLL_GetPriorRecord(self):
        """
        Check that the prior record is returned correctly, the index values
        are correct after the get, and the correct return codes are returned.

        @return: C{None}
        """
        # Test no records
        self._getPriorRecord(Info(), result=Return.NULL_LIST)
        # Test for curent record
        values = []
        values.append("ZZZZ - This is test record one.")
        values.append("AAAA - This is test record two.")

        for value in values:
            self._addRecord(Info(value))

        self._currentPointerToTail()
        self._getPriorRecord(Info(), test=values[0])
        self._getCurrentIndex(test=1)

    def test_DLL_GetNextRecord(self):
        """
        Check that the next record is returned correctly, the index values are
        correct after the get, and the correct return codes are returned.

        @return: C{None}
        """
        # Test no records
        self._getNextRecord(Info(), result=Return.NULL_LIST)
        # Test for curent record
        values = []
        values.append("ZZZZ - This is test record one.")
        values.append("AAAA - This is test record two.")

        for value in values:
            self._addRecord(Info(value))

        self._currentPointerToHead()
        self._getNextRecord(Info(), test=values[1])
        self._getCurrentIndex(test=2)

    def test_DLL_Save_LoadList(self):
        """
        Check that the list is saved and loaded correctly, the index values are
        correct after the loads, the sorting on load is done properly, and the
        correct return codes are returned.

        @return: C{None}
        """
        filePath = "/tmp/unittest.data"
        # Test no records
        self._saveList(filePath, result=Return.NULL_LIST)
        # Test saving list to dick
        values = []
        values.append("ZZZZ - This is test record one.")
        values.append("AAAA - This is test record two.")
        values.append("NNNN - This is test record three.")
        values.append("YYYY - This is test record four.")
        values.append("BBBB - This is test record five.")
        values.append("MMMM - This is test record six.")

        for value in values:
            self._addRecord(Info(value))

        self._getNumberOfRecords(test=6)
        self._saveList(filePath)
        # Test already has data in list.
        self._saveList(filePath, result=Return.NOT_MODIFIED)
        # Test load list.
        self._loadList(filePath, self._dll.compare())
        # The current index is an arbitrary number depending on the sort
        # algorithm used. This next test will fail in version 1.2.1 and below.
        self._getCurrentIndex(test=3)
        self._currentPointerToHead()
        self._getCurrentIndex(test=1)
        # Test open error.
        self._loadList("", self._dll.compare(), result=Return.OPEN_ERROR)
        self._getCurrentIndex(test=1)
        os.remove(filePath)

    #
    # Methods to interface into ctypes.
    #
    def _initList(self, infoSize):
        """
        Prepare the link list for use and asserts that there are no
        C{APIException} or C{FunctionException} exceptions, and the C{list_p}
        object is valid.

        @param infoSize: The size in bytes of the user defined C{Info} class.
        @type infoSize: C{int}
        @return: A pinter to the link list.
        @rtype: C{ctypes POINTER}
        """
        try:
            list_p = self._dll.create(infoSize)
        except APIException, e:
            self.fail(e)
        except FunctionException, e:
            self.fail(e)

        msg = "DLL_CreateList failed, list_p: %s."
        self.assertTrue(list_p not in (0, None),
                        msg=msg % hex(cast(list_p, c_void_p).value))
        return list_p

    def _destroyList(self):
        """
        Executes the C{destroyList} method and asserts that there are no
        C{APIException} exceptions.

        @return: C{None}
        """
        try:
            self._dll.destroyList()
        except APIException, e:
            self.fail(e)

    def _isListEmpty(self, test=True):
        """
        Executes the C{isListEmpty} method, asserts that there are no
        C{APIException} exceptions, and asserts that the returned value is
        correct.

        @keyword test: The expected value, the default is C{True}.
        @type test: C{bool}
        @return: C{None}
        """
        try:
            retval = self._dll.isListEmpty()
        except APIException, e:
            self.fail(e)

        msg = "retval: %s, test: %s"
        self.assertTrue(retval == test, msg=msg % (retval, test))

    def _isListFull(self, test=True):
        """
        Execute the C{isListFull} method, asserts that there are no
        C{APIException} exceptions, and asserts that the return value is
        correct.

        @keyword test: The expected value, the default is C{True}.
        @type test: C{bool}
        @return: C{None}
        """
        try:
            retval = self._dll.isListFull()
        except APIException, e:
            self.fail(e)

        msg = "retval: %s, test: %s"
        self.assertTrue(retval == test, msg=msg % (retval, test))

    def _getNumberOfRecords(self, test=0):
        """
        Execute the C{getNumberOfRecords} method, asserts that there are no
        C{APIException} exceptions, and asserts that the returned value is
        correct.

        @keyword test: The expected value, the default is C{0}.
        @type test: C{int}
        @return: C{None}
        """
        try:
            retval = self._dll.getNumberOfRecords()
        except APIException, e:
            self.fail(e)

        msg = "retval: %s, test: %s"
        self.assertTrue(retval == test, msg=msg % (retval, test))

    def _setSearchModes(self, origin, dir, result=Return.NORMAL):
        """
        Execute the C{setSearchModes} method, asserts that there are no
        C{APIException} or C{FunctionException} exceptions, and asserts that
        the return code is correct.

        @keyword result: The expected value, the default is C{Return.NORMAL}.
        @type result: C{Return}
        @return: C{None}
        """
        try:
            retval = self._dll.setSearchModes(origin, dir)
        except APIException, e:
            self.fail(e)
        except FunctionException, e:
            msg = "Return.%s: %s" % Return.getMessage(e.getRetval())
            self.assertTrue(e.getRetval() == result, msg=msg)

    def _getSearchModes(self, test=(SrchOrigin.HEAD, SrchDir.DOWN)):
        """
        Execute the C{getSearchModes} method, asserts that there are no
        C{APIException} exceptions, and asserts that the returned C{tuple} is
        correct.

        @keyword test: The expected value, the default is
                       C{(SrchOrigin.HEAD, SrchDir.DOWN)}.
        @type test: C{tuple} of C{SrchOrigin} and C{SrchDir}
        @return: C{None}
        """
        try:
            origin, direction = self._dll.getSearchModes()
        except APIException, e:
            self.fail(e)

        #self._dll._lib._printList(self._list_p)
        msg = "SrchOrigin.%s: %s" % SrchOrigin.getMessage(origin)
        self.assertTrue(origin == test[0], msg=msg)
        msg = "SrchDir.%s: %s" % SrchDir.getMessage(direction)
        self.assertTrue(direction == test[1], msg=msg)

    def _getCurrentIndex(self, test=0):
        """
        Execute the C{getCurrentIndex} method, asserts that there are no
        C{APIException} exceptions, and asserts that the returned value is
        correct.

        @keyword test: The expected value, the default is C{0}.
        @type test: C{int}
        @return: C{None}
        """
        try:
            retval = self._dll.getCurrentIndex()
        except APIException, e:
            self.fail(e)

        msg = "retval: %s, test: %s"
        self.assertTrue(retval == test, msg=msg % (retval, test))

    def _currentPointerToHead(self, result=Return.NORMAL):
        """
        Execute the C{currentPointerToHead} method, asserts that there are no
        C{APIException} or C{FunctionException} exceptions, and asserts that
        the return code is correct.

        @keyword result: The expected value, the default is C{Return.NORMAL}.
        @type result: C{Return}
        @return: C{None}
        """
        try:
            retval = self._dll.currentPointerToHead()
        except APIException, e:
            self.fail(e)
        except FunctionException, e:
            msg = "Return.%s: %s" % Return.getMessage(e.getRetval())
            self.assertTrue(e.getRetval() == result, msg=msg)

    def _currentPointerToTail(self, result=Return.NORMAL):
        """
        Execute the C{currentPointerToTail} method, asserts that there are no
        C{APIException} or C{FunctionException} exceptions, and asserts that
        the return code is correct.

        @keyword result: The expected value, the default is C{Return.NORMAL}.
        @type result: C{Return}
        @return: C{None}
        """
        try:
            retval = self._dll.currentPointerToTail()
        except APIException, e:
            self.fail(e)
        except FunctionException, e:
            msg = "Return.%s: %s" % Return.getMessage(e.getRetval())
            self.assertTrue(e.getRetval() == result, msg=msg)

    def _incrementCurrentPointer(self, result=Return.NORMAL):
        """
        Execute the C{incrementCurrentPointer} method, asserts that there are
        no C{APIException} or C{FunctionException} exceptions, and asserts that
        the return code is correct.

        @keyword result: The expected value, the default is C{Return.NORMAL}.
        @type result: C{Return}
        @return: C{None}
        """
        try:
            retval = self._dll.incrementCurrentPointer()
        except APIException, e:
            self.fail(e)
        except FunctionException, e:
            msg = "Return.%s: %s" % Return.getMessage(e.getRetval())
            self.assertTrue(e.getRetval() == result, msg=msg)

    def _decrementCurrentPointer(self, result=Return.NORMAL):
        """
        Execute the C{decrementCurrentPointer} method, asserts that there are
        no C{APIException} or C{FunctionException} exceptions, and asserts that
        the return code is correct.

        @keyword result: The expected value, the default is C{Return.NORMAL}.
        @type result: C{Return}
        @return: C{None}
        """
        try:
            retval = self._dll.decrementCurrentPointer()
        except APIException, e:
            self.fail(e)
        except FunctionException, e:
            msg = "Return.%s: %s" % Return.getMessage(e.getRetval())
            self.assertTrue(e.getRetval() == result, msg=msg)

    def _storeCurrentPointer(self, result=Return.NORMAL):
        """
        Execute the C{storeCurrentPointer} method, asserts that there are no
        C{APIException} or C{FunctionException} exceptions, and asserts that
        the return code is correct.

        @keyword result: The expected value, the default is C{Return.NORMAL}.
        @type result: C{Return}
        @return: C{None}
        """
        try:
            retval = self._dll.storeCurrentPointer()
        except APIException, e:
            self.fail(e)
        except FunctionException, e:
            msg = "Return.%s: %s" % Return.getMessage(e.getRetval())
            self.assertTrue(e.getRetval() == result, msg=msg)

    def _restoreCurrentPointer(self, result=Return.NORMAL):
        """
        Execute the C{restoreCurrentPointer} method, asserts that there are no
        C{APIException} or C{FunctionException} exceptions, and asserts that
        the return code is correct.

        @keyword result: The expected value, the default is C{Return.NORMAL}.
        @type result: C{Return}
        @return: C{None}
        """
        try:
            retval = self._dll.restoreCurrentPointer()
        except APIException, e:
            self.fail(e)
        except FunctionException, e:
            msg = "Return.%s: %s" % Return.getMessage(e.getRetval())
            self.assertTrue(e.getRetval() == result, msg=msg)

    def _addRecord(self, info, pFun=None, result=Return.NORMAL):
        """
        Execute the C{addRecord} method, asserts that there are no
        C{APIException} or C{FunctionException} exceptions, and asserts that
        the return code is correct.

        @param info: An instance of the C{Info} class.
        @type info: C{Info}
        @keyword pFun: An optional compare function, the default is C{None}.
        @type pFun: C{ctypes CFUNCTYPE}
        @keyword result: The expected value, the default is C{Return.NORMAL}.
        @type result: C{Return}
        @return: C{None}
        """
        try:
            retval = self._dll.addRecord(info, pFun=pFun)
        except APIException, e:
            self.fail(e)
        except FunctionException, e:
            msg = "Return.%s: %s" % Return.getMessage(e.getRetval())
            self.assertTrue(e.getRetval() == result, msg=msg)

    def _insertRecord(self, info, dir, result=Return.NORMAL):
        """
        Execute the C{insertRecord} method, asserts that there are no
        C{APIException} or C{FunctionException} exceptions, and asserts that
        the return code is correct.

        @param info: An instance of the C{Info} class.
        @type info: C{Info}
        @param dir: The direction to insert indicator.
        @type dir: C{InsertDir}
        @keyword result: The expected value, the default is C{Return.NORMAL}.
        @type result: C{Return}
        @return: C{None}
        """
        try:
            retval = self._dll.insertRecord(info, dir)
        except APIException, e:
            self.fail(e)
        except FunctionException, e:
            msg = "Return.%s: %s" % Return.getMessage(e.getRetval())
            self.assertTrue(e.getRetval() == result, msg=msg)

    def _swapRecord(self, dir, result=Return.NORMAL):
        """
        Execute the C{swapRecord} method, asserts that there are no
        C{APIException} or C{FunctionException} exceptions, and asserts that
        the return code is correct.

        @param dir: The direction to swap indicator.
        @type dir: C{InsertDir}
        @keyword result: The expected value, the default is C{Return.NORMAL}.
        @type result: C{Return}
        @return: C{None}
        """
        try:
            retval = self._dll.swapRecord(dir)
        except APIException, e:
            self.fail(e)
        except FunctionException, e:
            msg = "Return.%s: %s" % Return.getMessage(e.getRetval())
            self.assertTrue(e.getRetval() == result, msg=msg)

    def _updateCurrentRecord(self, record, result=Return.NORMAL):
        """
        Execute the C{updateCurrentRecord} method, asserts that there are no
        C{APIException} or C{FunctionException} exceptions, and asserts that
        the return code is correct.

        @param record: Will contains the results of the get.
        @type record: C{Info}
        @keyword result: The expected value, the default is C{Return.NORMAL}.
        @type result: C{Return}
        @return: C{None}
        """
        try:
            retval = self._dll.updateCurrentRecord(record)
        except APIException, e:
            self.fail(e)
        except FunctionException, e:
            msg = "Return.%s: %s" % Return.getMessage(e.getRetval())
            self.assertTrue(e.getRetval() == result, msg=msg)

    def _deleteCurrentRecord(self, result=Return.NORMAL):
        """
        Execute the C{} method, asserts that there are no
        C{APIException} or C{FunctionException} exceptions, and asserts that
        the return code is correct.

        @keyword result: The expected value, the default is C{Return.NORMAL}.
        @type result: C{Return}
        @return: C{None}
        """
        try:
            retval = self._dll.deleteCurrentRecord()
        except APIException, e:
            self.fail(e)
        except FunctionException, e:
            msg = "Return.%s: %s" % Return.getMessage(e.getRetval())
            self.assertTrue(e.getRetval() == result, msg=msg)

    def _deleteEntireList(self, result=Return.NORMAL):
        """
        Execute the C{deleteAllNodes} method, asserts that there are no
        C{APIException} or C{FunctionException} exceptions, and asserts that
        the return code is correct.

        @keyword result: The expected value, the default is C{Return.NORMAL}.
        @type result: C{Return}
        @return: C{None}
        """
        try:
            retval = self._dll.deleteAllNodes()
        except APIException, e:
            self.fail(e)
        except FunctionException, e:
            msg = "Return.%s: %s" % Return.getMessage(e.getRetval())
            self.assertTrue(e.getRetval() == result, msg=msg)

    def _findRecord(self, record, match, pFun=None, result=Return.NORMAL):
        """
        Execute the C{findRecord} method, asserts that there are no
        C{APIException} or C{FunctionException} exceptions, assert that the
        test value is correct, and asserts that the return code is correct.

        @param record:  Will contain the results of the find.
        @type record: C{Info}
        @param match: Provides the query information.
        @type match: C{Info}
        @keyword pFun: An optional compare function, the default is C{None}.
        @type pFun: C{ctypes CFUNCTYPE}
        @keyword result: The expected value, the default is C{Return.NORMAL}.
        @type result: C{Return}
        @return: C{None}
        """
        try:
            retval = self._dll.findRecord(record, match, pFun=pFun)
        except APIException, e:
            self.fail(e)
        except FunctionException, e:
            msg = "Return.%s: %s" % Return.getMessage(e.getRetval())
            self.assertTrue(e.getRetval() == result, msg=msg)

        msg = "record.value: %s, match.value: %s" % (record.value, match.value)
        self.assertTrue(record.value == match.value or
                        result == Return.NOT_FOUND, msg=msg)

    def _findNthRecord(self, record, skip, test="", result=Return.NORMAL):
        """
        Execute the C{findNthRecord} method, asserts that there are no
        C{APIException} or C{FunctionException} exceptions, assert that the
        test value is correct, and asserts that the return code is correct.

        @param record:  Will contain the results of the find.
        @type record: C{Info}
        @param skip: The number of records to skip over.
        @type skip: C{int}
        @keyword test: Value to test, default is an empty string.
        @type test: C{str}
        @keyword result: The expected value, the default is C{Return.NORMAL}.
        @type result: C{Return}
        @return: C{None}
        """
        try:
            retval = self._dll.findNthRecord(record, skip)
        except APIException, e:
            self.fail(e)
        except FunctionException, e:
            msg = "Return.%s: %s" % Return.getMessage(e.getRetval())
            self.assertTrue(e.getRetval() == result, msg=msg)

        #print "record.value: %s, test: %s" % (record.value, test)
        msg = "record.value: %s, test: %s" % (record.value, test)
        self.assertTrue(record.value == test or
                        result == Return.NOT_FOUND, msg=msg)

    def _getCurrentRecord(self, record, test="", result=Return.NORMAL):
        """
        Execute the C{getCurrentRecord} method, asserts that there are no
        C{APIException} or C{FunctionException} exceptions, assert that the
        test value is correct, and asserts that the return code is correct.

        @param record:  Will contain the results of the find.
        @type record: C{Info}
        @keyword test: Value to test, default is an empty string.
        @type test: C{str}
        @keyword result: The expected value, the default is C{Return.NORMAL}.
        @type result: C{Return}
        @return: C{None}
        """
        try:
            retval = self._dll.getCurrentRecord(record)
        except APIException, e:
            self.fail(e)
        except FunctionException, e:
            msg = "Return.%s: %s" % Return.getMessage(e.getRetval())
            self.assertTrue(e.getRetval() == result, msg=msg)

        msg = "record.value: %s, test: %s" % (record.value, test)
        self.assertTrue(test == record.value, msg=msg)

    def _getPriorRecord(self, record, test="", result=Return.NORMAL):
        """
        Execute the C{getPriorRecord} method, asserts that there are no
        C{APIException} or C{FunctionException} exceptions, assert that the
        test value is correct, and asserts that the return code is correct.

        @param record:  Will contain the results of the find.
        @type record: C{Info}
        @keyword test: Value to test, default is an empty string.
        @type test: C{str}
        @keyword result: The expected value, the default is C{Return.NORMAL}.
        @type result: C{Return}
        @return: C{None}
        """
        try:
            retval = self._dll.getPriorRecord(record)
        except APIException, e:
            self.fail(e)
        except FunctionException, e:
            msg = "Return.%s: %s" % Return.getMessage(e.getRetval())
            self.assertTrue(e.getRetval() == result, msg=msg)

        msg = "record.value: %s, test: %s" % (record.value, test)
        self.assertTrue(test == record.value, msg=msg)

    def _getNextRecord(self, record, test="", result=Return.NORMAL):
        """
        Execute the C{getNextRecord} method, asserts that there are no
        C{APIException} or C{FunctionException} exceptions, assert that the
        test value is correct, and asserts that the return code is correct.

        @param record:  Will contain the results of the find.
        @type record: C{Info}
        @keyword test: Value to test, default is an empty string.
        @type test: C{str}
        @keyword result: The expected value, the default is C{Return.NORMAL}.
        @type result: C{Return}
        @return: C{None}
        """
        try:
            retval = self._dll.getNextRecord(record)
        except APIException, e:
            self.fail(e)
        except FunctionException, e:
            msg = "Return.%s: %s" % Return.getMessage(e.getRetval())
            self.assertTrue(e.getRetval() == result, msg=msg)

        msg = "record.value: %s, test: %s" % (record.value, test)
        self.assertTrue(test == record.value, msg=msg)

    def _saveList(self, path, result=Return.NORMAL):
        """
        Execute the C{saveList} method, asserts that there are no
        C{APIException} or C{FunctionException} exceptions, and asserts that
        the return code is correct.

        @param path: The full path to the data file.
        @type path: C{str}
        @keyword result: The expected value, the default is C{Return.NORMAL}.
        @type result: C{Return}
        @return: C{None}
        """
        try:
            retval = self._dll.saveList(path)
        except APIException, e:
            self.fail(e)
        except FunctionException, e:
            msg = "Return.%s: %s" % Return.getMessage(e.getRetval())
            self.assertTrue(e.getRetval() == result, msg=msg)

    def _loadList(self, path, pFun=None, result=Return.NORMAL):
        """
        Execute the C{loadList} method, asserts that there are no
        C{APIException} or C{FunctionException} exceptions, and asserts that
        the return code is correct.

        @param path: The full path to the data file.
        @type path: C{str}
        @keyword pFun: An optional compare function, the default is C{None}.
        @type pFun: C{ctypes CFUNCTYPE}
        @keyword result: The expected value, the default is C{Return.NORMAL}.
        @type result: C{Return}
        @return: C{None}
        """
        try:
            retval = self._dll.loadList(path, pFun=pFun)
        except APIException, e:
            self.fail(e)
        except FunctionException, e:
            msg = "Return.%s: %s" % Return.getMessage(e.getRetval())
            self.assertTrue(e.getRetval() == result, msg=msg)


if __name__ == '__main__':
    unittest.main()
