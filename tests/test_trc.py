import os
import unittest

from trc import TRCData
try:
    from .data_store import TEST_DATA_01, TEST_DATA_02, TEST_DATA_03, TEST_DATA_04,\
        TEST_DATA_05, TEST_DATA_06, TEST_DATA_07
except ImportError:
    from data_store import TEST_DATA_01, TEST_DATA_02, TEST_DATA_03, TEST_DATA_04, \
        TEST_DATA_05, TEST_DATA_06, TEST_DATA_07

here = os.path.dirname(os.path.realpath(__file__))
resource_path = os.path.join(here, 'resources')


class TestTRCResources(unittest.TestCase):

    def test_load_file_01(self):
        data = TRCData()
        data.load(os.path.join(resource_path, 'test_file_01.trc'))
        self.assertIn('FileName', data)
        self.assertEqual(4, data['NumFrames'])
        self.assertEqual(4, len(data['Markers']))

    def test_load_file_02(self):
        data = TRCData()
        data.load(os.path.join(resource_path, 'test_file_02.trc'))
        self.assertIn('FileName', data)
        self.assertEqual(936, data['NumFrames'])
        self.assertEqual(39, len(data['Markers']))

    def test_load_file_03(self):
        data = TRCData()
        data.load(os.path.join(resource_path, 'test_file_03.trc'))
        self.assertIn('FileName', data)
        self.assertEqual(466, data['NumFrames'])
        self.assertEqual(48, len(data['Markers']))


class TestTRCData(unittest.TestCase):

    def test_parse_data_01(self):
        data = TRCData()
        data.parse(TEST_DATA_01)
        self.assertIn('FileName', data)
        self.assertEqual(4, data['NumFrames'])
        self.assertEqual(4, len(data['Markers']))

    def test_parse_data_02(self):
        data = TRCData()
        with self.assertRaises(IOError):
            data.parse(TEST_DATA_02)

    def test_parse_data_03(self):
        data = TRCData()
        with self.assertRaises(IOError):
            data.parse(TEST_DATA_03)

    def test_parse_data_04(self):
        data = TRCData()
        with self.assertRaises(IOError):
            data.parse(TEST_DATA_04)

    def test_parse_data_05(self):
        data = TRCData()
        with self.assertRaises(IOError):
            data.parse(TEST_DATA_05)

    def test_parse_data_06(self):
        data = TRCData()
        with self.assertRaises(IOError):
            data.parse(TEST_DATA_06)

    def test_parse_data_07(self):
        data = TRCData()
        with self.assertRaises(IOError):
            data.parse(TEST_DATA_07)


if __name__ == '__main__':
    unittest.main()
