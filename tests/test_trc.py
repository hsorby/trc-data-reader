import os
import unittest

from trc import TRCData

try:
    from .data_store import TEST_DATA_01, TEST_DATA_02, TEST_DATA_03, TEST_DATA_04, \
        TEST_DATA_05, TEST_DATA_06, TEST_DATA_07, TEST_DATA_08, TEST_DATA_09, TEST_DATA_10, \
        TEST_DATA_11
except ImportError:
    from data_store import TEST_DATA_01, TEST_DATA_02, TEST_DATA_03, TEST_DATA_04, \
        TEST_DATA_05, TEST_DATA_06, TEST_DATA_07, TEST_DATA_08, TEST_DATA_09, TEST_DATA_10, \
        TEST_DATA_11

here = os.path.dirname(os.path.realpath(__file__))
resource_path = os.path.join(here, 'resources')


class TestTRCResources(unittest.TestCase):

    def test_load_file_01(self):
        data = TRCData()
        data.load(os.path.join(resource_path, 'test_file_01.trc'))
        self.assertIn('FileName', data)
        self.assertEqual(4, data['NumFrames'])
        self.assertEqual(2, len(data['Markers']))

    def test_load_file_02(self):
        data = TRCData()
        data.load(os.path.join(resource_path, 'test_file_02.trc'))
        self.assertIn('FileName', data)
        self.assertEqual(936, data['NumFrames'])
        self.assertEqual(37, len(data['Markers']))

    def test_load_file_03(self):
        data = TRCData()
        data.load(os.path.join(resource_path, 'test_file_03.trc'))
        self.assertIn('FileName', data)
        self.assertEqual(466, data['NumFrames'])
        self.assertEqual(46, len(data['Markers']))

    def test_load_file_04(self):
        data = TRCData()
        data.load(os.path.join(resource_path, 'test_file_04.trc'))
        self.assertIn('FileName', data)
        self.assertEqual(2, data['NumFrames'])
        self.assertEqual(37, len(data['Markers']))

    def test_load_file_05(self):
        data = TRCData()
        data.load(os.path.join(resource_path, 'test_file_05.trc'))

        # Check that we have correctly loaded the missing coordinates.
        self.assertIn('FileName', data)
        self.assertEqual(4, data['NumFrames'])
        self.assertEqual(8, len(data['Markers']))


class TestC3DImport(unittest.TestCase):

    def test_import_file_01(self):
        data = TRCData()
        data.import_from(os.path.join(resource_path, 'c3d_test_file_01.c3d'))
        self.assertIn('FileName', data)
        self.assertEqual(8, data['NumFrames'])
        self.assertEqual(8, len(data['Markers']))

    def test_import_file_02(self):
        data = TRCData()
        data.import_from(os.path.join(resource_path, 'c3d_test_file_02.c3d'))
        self.assertIn('FileName', data)
        self.assertEqual(100, data['NumFrames'])
        self.assertEqual(75, len(data['Markers']))

    def test_import_file_03(self):
        data = TRCData()
        data.import_from(os.path.join(resource_path, 'c3d_test_file_03.c3d'))

        # Check that we have correctly imported the missing coordinates.
        self.assertIn('FileName', data)
        self.assertEqual(4, data['NumFrames'])
        self.assertEqual(8, len(data['Markers']))


class TestTRCData(unittest.TestCase):

    def test_parse_data_01(self):
        data = TRCData()
        data.parse(TEST_DATA_01)
        self.assertIn('FileName', data)
        self.assertEqual(4, data['NumFrames'])
        self.assertEqual(2, len(data['Markers']))

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

    def test_parse_data_08(self):
        data = TRCData()
        data.parse(TEST_DATA_08)
        self.assertIn('FileName', data)
        self.assertEqual(4, data['NumFrames'])
        self.assertEqual(2, len(data['Markers']))

    def test_parse_data_09(self):
        data = TRCData()
        with self.assertRaises(IOError):
            data.parse(TEST_DATA_09)

    def test_parse_data_10(self):
        data = TRCData()
        data.parse(TEST_DATA_10)
        self.assertIn('FileName', data)
        self.assertEqual(2, data['NumFrames'])
        self.assertEqual(37, len(data['Markers']))

    def test_parse_data_11(self):
        # Test parsing a file with "non-native" line endings.
        data = TRCData()
        data.parse(TEST_DATA_11, line_sep='\r\n')
        self.assertIn('FileName', data)
        self.assertEqual(2, data['NumFrames'])
        self.assertEqual(2, len(data['Markers']))


class TestStoreTRC(unittest.TestCase):

    def test_save_file_01(self):
        output_file = os.path.join(resource_path, 'test_file_01_out.trc')
        data_orig = TRCData()
        data_orig.load(os.path.join(resource_path, 'test_file_01.trc'))
        data_orig.save(output_file)

        data_copy = TRCData()
        data_copy.load(output_file)

        self.assertEqual(data_orig['NumFrames'], data_copy['NumFrames'])
        self.assertEqual(len(data_orig['Markers']), len(data_copy['Markers']))

        os.remove(output_file)

    def test_save_file_02(self):
        data = TRCData()
        with self.assertRaises(NotImplementedError):
            data.save(os.path.join(resource_path, 'never_exists.trc'))

    def test_save_file_03(self):
        data = TRCData()
        data['PathFileType'] = '3'
        data['DataFormat'] = 'X'
        data['FileName'] = 'never_exists.trc'
        with self.assertRaises(KeyError):
            data.save(os.path.join(resource_path, 'never_exists.trc'))

    def test_save_file_04(self):
        output_file = os.path.join(resource_path, 'c3d_test_file_01_out.trc')
        data_orig = TRCData()
        data_orig.import_from(os.path.join(resource_path, 'c3d_test_file_01.c3d'))
        data_orig.save(output_file)

        data_copy = TRCData()
        data_copy.load(output_file)

        self.assertEqual(data_orig['NumFrames'], data_copy['NumFrames'])
        self.assertEqual(len(data_orig['Markers']), len(data_copy['Markers']))

        os.remove(output_file)

    def test_save_file_05(self):
        output_file = os.path.join(resource_path, 'c3d_test_file_03_out.trc')
        data = TRCData()
        data.import_from(os.path.join(resource_path, 'c3d_test_file_03.c3d'))
        data.save(output_file)

        # Check that the missing coordinates were written as empty strings.
        with open(output_file, 'r') as file:
            lines = file.readlines()
        for line in lines[6:]:
            values = line.strip('\n').strip('\r').split('\t')
            self.assertEqual(26, len(values))
            self.assertEqual(12, values.count(''))

        os.remove(output_file)


if __name__ == '__main__':
    unittest.main()
