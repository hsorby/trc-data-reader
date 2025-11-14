import io
import os
import unittest
from contextlib import redirect_stdout

from trc import TRCData, TRCFormatError

try:
    from .data_store import TEST_DATA_01, TEST_DATA_02, TEST_DATA_03, TEST_DATA_04, \
        TEST_DATA_05, TEST_DATA_06, TEST_DATA_07, TEST_DATA_08, TEST_DATA_09, TEST_DATA_10, \
        TEST_DATA_11, TEST_DATA_12
except ImportError:
    from data_store import TEST_DATA_01, TEST_DATA_02, TEST_DATA_03, TEST_DATA_04, \
        TEST_DATA_05, TEST_DATA_06, TEST_DATA_07, TEST_DATA_08, TEST_DATA_09, TEST_DATA_10, \
        TEST_DATA_11, TEST_DATA_12

here = os.path.dirname(os.path.realpath(__file__))
resource_path = os.path.join(here, 'resources')


class TestTRCResources(unittest.TestCase):

    def test_load_file_01(self):
        data = TRCData()
        data.load(os.path.join(resource_path, 'test_file_01.trc'))
        self.assertIn('FileName', data)
        self.assertEqual(4, data['NumFrames'])
        self.assertEqual(2, len(data['Markers']))
        self.assertEqual('HeadTop', data['Markers'][0])
        self.assertEqual('ForeHead', data['Markers'][1])

        expected_data = [
            (0.000, [[-2894.1709, 1663.1084, -3255.51221], [-2830.51074, 1535.71509, -3161.38867]]),
            (0.017, [[-2894.22632, 1663.09448, -3255.7373], [-2830.58838, 1535.5957, -3161.22119]]),
            (0.033, [[-2894.30054, 1663.0531, -3255.97241], [-2830.67212, 1535.46863, -3161.08936]]),
            (0.050, [[-2894.37915, 1662.97754, -3256.2356], [-2830.76855, 1535.33289, -3161.00732]]),
        ]
        for i in range(1, 5):
            expected_time = expected_data[i - 1][0]
            expected_values = expected_data[i - 1][1]
            time, values = data[i]
            self.assertEqual(expected_time, time)
            self.assertEqual(expected_values, values)

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

    def test_load_file_03a(self):
        f = io.StringIO()

        data = TRCData()
        with redirect_stdout(f):
            data.load(os.path.join(resource_path, 'test_file_03.trc'), verbose=True)

        captured_output = f.getvalue()
        self.assertIn('Bad data line, frame: 134, time: 2.217, expected entries: 138, actual entries: 141', captured_output)

    def test_load_file_04(self):
        data = TRCData()
        data.load(os.path.join(resource_path, 'test_file_04.trc'))
        self.assertIn('FileName', data)
        self.assertEqual(2, data['NumFrames'])
        self.assertEqual(37, len(data['Markers']))

    def test_load_file_05(self):
        data = TRCData()
        data.load(os.path.join(resource_path, 'test_file_05.trc'))
        self.assertIn('FileName', data)

        # Check that we have correctly loaded the missing coordinates.
        self.assertIn('FileName', data)
        self.assertEqual(4, data['NumFrames'])
        self.assertEqual(8, len(data['Markers']))

    def test_load_file_06(self):
        data = TRCData()
        data.load(os.path.join(resource_path, 'test_file_06_2tab_one_space.trc'))

        # Check that we have correctly loaded the missing coordinates.
        self.assertIn('FileName', data)
        self.assertEqual(1091, data['NumFrames'])
        self.assertEqual(9, len(data['Markers']))


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
        with self.assertRaises(TRCFormatError):
            data.parse(TEST_DATA_02)

    def test_parse_data_03(self):
        data = TRCData()
        with self.assertRaises(TRCFormatError):
            data.parse(TEST_DATA_03)

    def test_parse_data_04(self):
        data = TRCData()
        with self.assertRaises(TRCFormatError):
            data.parse(TEST_DATA_04)

    def test_parse_data_05(self):
        data = TRCData()
        with self.assertRaises(TRCFormatError):
            data.parse(TEST_DATA_05)

    def test_parse_data_06(self):
        data = TRCData()
        with self.assertRaises(TRCFormatError):
            data.parse(TEST_DATA_06)

    def test_parse_data_07(self):
        data = TRCData()
        with self.assertRaises(TRCFormatError):
            data.parse(TEST_DATA_07)

    def test_parse_data_08(self):
        data = TRCData()
        data.parse(TEST_DATA_08)
        self.assertIn('FileName', data)
        self.assertEqual(4, data['NumFrames'])
        self.assertEqual(2, len(data['Markers']))

    def test_parse_data_09(self):
        data = TRCData()
        with self.assertRaises(TRCFormatError):
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

    def test_parse_data_12(self):
        # Test parsing a file with missing data at the end of the line.
        data = TRCData()
        data.parse(TEST_DATA_12)
        self.assertIn('FileName', data)
        self.assertEqual(3, data['NumFrames'])
        self.assertEqual(9, len(data['Markers']))

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

    def test_save_file_06(self):
        output_file = os.path.join(resource_path, 'c3d_test_file_03_out.trc')
        data = TRCData()
        data.import_from(os.path.join(resource_path, 'c3d_test_file_03.c3d'))
        data.save(output_file, add_trailing_tab=True)

        # Check that the missing coordinates were written as empty strings.
        with open(output_file, 'r') as file:
            lines = file.readlines()
        for line in lines[6:]:
            values = line.strip('\n').strip('\r').split('\t')
            self.assertEqual(27, len(values))
            self.assertEqual(13, values.count(''))

        os.remove(output_file)


if __name__ == '__main__':
    unittest.main()
