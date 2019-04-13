import unittest

from TotalDepth.common.Rle import RLE


class TestRle(unittest.TestCase):
    """Tests ..."""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def testSetUpTearDown(self):
        """TestCLass: Tests setUp() and tearDown()."""
        pass

    def test_00(self):
        """TestRle.test_00(): Basic test, single range."""
        myR = RLE()
        myInput = range(0, 3*8, 3)
        for v in myInput:
            myR.add(v)
        self.assertEqual(len(myR), 1)
        self.assertEqual(myR.numValues(), len(myInput))
        self.assertEqual([aV for aV in myR.values()], list(myInput))
        for i, v in enumerate(myInput):
            self.assertEqual(myR.value(i), v)
        # Check property access
        self.assertEqual(myR[0].datum, 0)
        self.assertEqual(myR[0].stride, 3)
        self.assertEqual(myR[0].repeat, 7)

    def test_00_00(self):
        """TestRle.test_00_00(): Basic test, empty."""
        myR = RLE()
        self.assertEqual(len(myR), 0)
        self.assertEqual(myR.numValues(), 0)
        self.assertEqual([aV for aV in myR.values()], [])
        self.assertRaises(IndexError, myR.value, 0)

    def test_00_01(self):
        """TestRle.test_00_01(): Basic test, single value."""
        myR = RLE()
        myR.add(8)
        self.assertEqual(len(myR), 1)
        self.assertEqual(myR.numValues(), 1)
        self.assertEqual([aV for aV in myR.values()], [8, ])
        self.assertEqual(myR.value(0), 8)
        # Check property access
        self.assertEqual(myR[0].datum, 8)
        self.assertEqual(myR[0].stride, None)
        self.assertEqual(myR[0].repeat, 0)

    def test_01(self):
        """TestRle.test_01(): Basic test, multiple ranges."""
        myR = RLE()
        myInput = list(range(0, 3*8, 3)) + list(range(72, 95, 1)) + list(range(105, 117, 2))
        for v in myInput:
            myR.add(v)
        # Three ranges
        self.assertEqual(len(myR), 3)
        self.assertEqual(myR.numValues(), len(myInput))
        self.assertEqual([aV for aV in myR.values()], myInput)
        for i, v in enumerate(myInput):
            self.assertEqual(myR.value(i), v)
        # Check property access
        self.assertEqual(myR[0].datum, 0)
        self.assertEqual(myR[0].stride, 3)
        self.assertEqual(myR[0].repeat, 7)
        self.assertEqual(myR[1].datum, 72)
        self.assertEqual(myR[1].stride, 1)
        self.assertEqual(myR[1].repeat, 95-72-1)
        self.assertEqual(myR[2].datum, 105)
        self.assertEqual(myR[2].stride, 2)
        self.assertEqual(myR[2].repeat, ((117-105)//2)-1)
        #print()
        #print(myR)
        str(myR)
#        self.assertEqual(
#            str(myR),
#            """RLE: func=None
#  RLEItem: datum=0 stride=3 repeat=7
#  RLEItem: datum=72 stride=1 repeat=22
#  RLEItem: datum=105 stride=2 repeat=5""")

    def test_02(self):
        """TestRle.test_02(): Basic test, single range, negative indexing."""
        myR = RLE()
        myInput = range(0, 3*8, 3)
        for v in myInput:
            myR.add(v)
        self.assertEqual(len(myR), 1)
        self.assertEqual([aV for aV in myR.values()], list(myInput))
        # Check property access
        self.assertEqual(myR[0].datum, 0)
        self.assertEqual(myR[0].stride, 3)
        self.assertEqual(myR[0].repeat, 7)
        # Test access from end
        myList = list(myInput)
        #print(myList)
        for i in range(-1, -1*(len(myInput)+1), -1):
            #print(i, myList[i], myR.value(i))
            self.assertEqual(myR.value(i), myList[i])

    def test_03(self):
        """TestRle.test_03(): Basic test, multiple ranges, negative indexing."""
        myR = RLE()
        #myInput = list(range(0, 3*2, 3)) + list(range(72, 75, 1)) + list(range(105, 109, 2))
        myInput = list(range(0, 3*8, 3)) + list(range(72, 95, 1)) + list(range(105, 117, 2))
        for v in myInput:
            myR.add(v)
        # Three ranges
        self.assertEqual(len(myR), 3)
        self.assertEqual(myR.numValues(), len(myInput))
        self.assertEqual([aV for aV in myR.values()], myInput)
        myList = list(myInput)
        #print(myList)
        for i in range(-1, -1*(len(myInput)+1), -1):
            #print(i, myList[i], myR.value(i))
            self.assertEqual(myR.value(i), myList[i])

    def test_04(self):
        """TestRle.test_04(): Basic test, single range of constant numbers."""
        myR = RLE()
        v = 1
        for v in range(4):
            myR.add(1)
        self.assertEqual(len(myR), 1)
        self.assertEqual(myR.numValues(), 4)
        self.assertEqual([aV for aV in myR.values()], [1,1,1,1])
        for i, v in enumerate(range(4)):
            self.assertEqual(myR.value(i), 1)
        # Check property access
        self.assertEqual(myR[0].datum, 1)
        self.assertEqual(myR[0].stride, 0)
        self.assertEqual(myR[0].repeat, 3)

    def test_05(self):
        """TestRle.test_05(): Basic test, multiple ranges, first/last and range recovery."""
        myR = RLE()
        myInput = list(range(0, 3*8, 3)) + list(range(72, 95, 1)) + list(range(105, 117, 2))
        for v in myInput:
            myR.add(v)
        # Three ranges
        self.assertEqual(len(myR), 3)
        self.assertEqual(myR.numValues(), len(myInput))
        self.assertEqual([aV for aV in myR.values()], myInput)
        myList = list(myInput)
        #print()
        #print(myList)
        for i in range(-1, -1*(len(myInput)+1), -1):
            #print(i, myList[i], myR.value(i))
            self.assertEqual(myR.value(i), myList[i])
        #print(myR.rangeList())
        #print([list(r) for r in myR.rangeList()])
        # Can not do direct range() comparison
        self.assertEqual(
            [
                list(range(0, 24, 3)),
                list(range(72, 95)),
                list(range(105, 117, 2))
            ],
            [list(r) for r in myR.rangeList()]
        )
        #print(myR.first())
        self.assertEqual(0, myR.first())
        #print(myR.last())
        self.assertEqual(115, myR.last())


class TestRleFunction(unittest.TestCase):
    """Tests ..."""
    def setUp(self):
        """Set up."""
        pass

    def tearDown(self):
        """Tear down."""
        pass

    def testSetUpTearDown(self):
        """TestRleFunction: Tests setUp() and tearDown()."""
        pass

    def test_00(self):
        """TestRleFunction.test_00(): Basic test, single range."""
        myR = RLE()
        myInput = range(0, 3*8, 3)
        for v in myInput:
            myR.add(v)
        self.assertEqual(len(myR), 1)
        self.assertEqual(myR.numValues(), len(myInput))
        self.assertEqual([aV for aV in myR.values()], list(myInput))
        for i, v in enumerate(myInput):
            self.assertEqual(myR.value(i), v)
        # Check property access
        self.assertEqual(myR[0].datum, 0)
        self.assertEqual(myR[0].stride, 3)
        self.assertEqual(myR[0].repeat, 7)

    def test_01(self):
        """TestRleFunction.test_01(): Basic test, multiple ranges."""
        myR = RLE(int)
        myInput = [str(v) for v in list(range(0, 3*8, 3)) + list(range(72, 95, 1)) + list(range(105, 117, 2))]
        for v in myInput:
            myR.add(v)
        # Three ranges
        self.assertEqual(len(myR), 3)
        self.assertEqual(myR.numValues(), len(myInput))
        self.assertEqual([str(aV) for aV in myR.values()], myInput)
        for i, v in enumerate(myInput):
            self.assertEqual(myR.value(i), int(v))
        # Check property access
        self.assertEqual(myR[0].datum, 0)
        self.assertEqual(myR[0].stride, 3)
        self.assertEqual(myR[0].repeat, 7)
        self.assertEqual(myR[1].datum, 72)
        self.assertEqual(myR[1].stride, 1)
        self.assertEqual(myR[1].repeat, 95-72-1)
        self.assertEqual(myR[2].datum, 105)
        self.assertEqual(myR[2].stride, 2)
        self.assertEqual(myR[2].repeat, ((117-105)//2)-1)
