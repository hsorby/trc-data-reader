import os
import re
import math

import c3d

_REQUIRED_HEADER_KEYS = ['DataRate', 'CameraRate', 'NumFrames', 'NumMarkers', 'Units', 'OrigDataRate']
_HEADER_KEYS = ['DataRate', 'CameraRate', 'NumFrames', 'NumMarkers', 'Units', 'OrigDataRate', 'OrigDataStartFrame',
                'OrigNumFrames']
_HEADER_TYPES = [float, float, int, int, str, float, int, int]
_COORDINATE_LABELS = ['X', 'Y', 'Z']


def _convert_header_key_value_to_type(key, value):
    index = _HEADER_KEYS.index(key)
    if _HEADER_TYPES[index] is float:
        return float(value)
    elif _HEADER_TYPES[index] is int:
        return int(value)

    return str(value)


def _convert_to_number(string):
    try:
        num = float(string)
    except ValueError:
        num = float('nan')
    return num


def _convert_coordinates(coordinates):
    return [_convert_to_number(value) for value in coordinates]


class TRCData(dict):
    """
    A trc data object when populated via 'load' or 'parse' contains motion capture data.
    For a valid trc file the following keys will be present (among others):
     - FileName
     - DataFormat
     - Markers
     - DataRate
     - NumFrames
     - NumMarkers

     Each marker found in the header part of the data will be a key in the dictionary containing a list
     of the coordinates for that label at each frame.
    """

    def _append_per_label_data(self, markers, data):
        for index, marker_data in enumerate(data):
            self[markers[index]] += [marker_data]

    def _process_contents(self, contents, verbose):
        markers = []
        file_header_keys = []
        data_header_markers = []
        data_format_count = 0
        header_read_successfully = False
        current_line_number = 0
        for line in contents:
            current_line_number += 1
            line = line.strip()
            if current_line_number == 1:
                # File Header 1
                sections = line.split(maxsplit=3)
                if len(sections) != 4:
                    raise IOError('File format invalid: Header line 1 does not have four tab delimited sections.')
                self[sections[0]] = sections[1]
                self['DataFormat'] = sections[2]
                data_format_count = len(sections[2].split('/'))
                self['FileName'] = sections[3]
            elif current_line_number == 2:
                # File Header 2
                file_header_keys = line.split()
            elif current_line_number == 3:
                # File Header 3
                file_header_data = line.split()
                if len(file_header_keys) == len(file_header_data):
                    for index, key in enumerate(file_header_keys):
                        if key == 'Units':
                            self[key] = file_header_data[index]
                        else:
                            self[key] = float(file_header_data[index])
                else:
                    raise IOError('File format invalid: File header keys count (%d) is not equal to file header '
                                  'data count (%d)' % (len(file_header_keys), len(file_header_data)))
            elif current_line_number == 4:
                # Data Header 1
                data_header_markers = line.split()
                if data_header_markers[0] != 'Frame#':
                    raise IOError('File format invalid: Data header does not start with "Frame#".')
                if data_header_markers[1] != 'Time':
                    raise IOError('File format invalid: Data header in position 2 is not "Time".')

                self['Frame#'] = []
                self['Time'] = []
            elif current_line_number == 5:
                # Data Header 1
                data_header_sub_marker = line.split()
                expected_sub_markers = int(self['NumMarkers']) * data_format_count

                if expected_sub_markers != len(data_header_sub_marker):
                    raise IOError('File format invalid: Data header marker count (%d) is not equal to data header '
                                  'sub-marker count (%d)' % (len(data_header_markers), len(data_header_sub_marker)))

                # Remove 'Frame#' and 'Time' from array of markers.
                data_header_markers.pop(0)
                data_header_markers.pop(0)
                markers = []
                for marker in data_header_markers:
                    marker = marker.strip()
                    if len(marker):
                        self[marker] = []
                        markers.append(marker)

                self['Markers'] = markers
            elif current_line_number == 6 and len(line) == 0:
                # Blank line
                header_read_successfully = True
            else:
                # Some files don't have a blank line at line six
                if current_line_number == 6:
                    header_read_successfully = True
                # Data section
                if header_read_successfully:
                    sections = line.split()

                    try:
                        frame = int(sections.pop(0))
                        self['Frame#'].append(frame)
                    except IndexError:
                        if int(self['NumFrames']) == len(self['Frame#']):
                            # We have reached the end of the specified frames
                            continue
                    except ValueError:
                        raise IOError(
                            f"File format invalid: "
                            f"Data frame length is {len(self['Frame#'])}, "
                            f"Expected {self['NumFrames']} frames."
                        )

                    time = float(sections.pop(0))
                    self['Time'].append(time)

                    line_data = [[float('nan')] * data_format_count] * int(self['NumMarkers'])
                    len_section = len(sections)
                    expected_entries = len(line_data) * data_format_count
                    if len_section > expected_entries:
                        if verbose:
                            print(f'Bad data line, frame: {frame}, time: {time}, expected entries: {expected_entries},'
                                  f' actual entries: {len_section}')
                        self[frame] = (time, line_data)
                        self._append_per_label_data(markers, line_data)
                    elif len_section % data_format_count == 0:
                        for index, place in enumerate(range(0, len_section, data_format_count)):
                            coordinates = _convert_coordinates(sections[place:place + data_format_count])
                            line_data[index] = coordinates

                        self[frame] = (time, line_data)
                        self._append_per_label_data(markers, line_data)
                    else:
                        raise IOError('File format invalid: Data frame %d does not match the data format' % len_section)

    def parse(self, data, line_sep=os.linesep, verbose=False):
        """
        Parse trc formatted motion capture data into a dictionary like object.

        :param data: The multi-line string of the data to parse.
        :param line_sep: The line separator to split lines with.
        :param verbose: Boolean for having verbose output, default is False.
        """
        contents = data.split(line_sep)
        if len(contents) == 1:
            data.replace('\r\n', '\n')
            contents = data.split('\n')
        self._process_contents(contents, verbose)

    def load(self, filename, encoding="utf-8", errors="strict", verbose=False):
        """
        Load a trc motion capture data file into a dictionary like object.

        :param filename: The name of the file to load.
        :param encoding: Default encoding is 'utf-8', see https://docs.python.org/3/library/codecs.html#standard-encodings.
        :param errors: Default error handling is 'strict',see https://docs.python.org/3/library/codecs.html#error-handlers.
        :param verbose: Boolean for having verbose output, default is False.
        """
        with open(filename, 'rb') as f:
            contents = f.read().decode(encoding=encoding, errors=errors)

        contents = contents.split(os.linesep)
        self._process_contents(contents, verbose)

    def _import_from_c3d(self, filename, filter_output=None, label_params=None):
        """
        Extracts TRC data from a C3D file.

        :param filename: The C3D file to be parsed.
        :param filter_output: Optional; A list of model-output parameters to be filtered out from
            the list of marker labels (e.g., ANGLES, FORCES, MOMENTS, POWERS, SCALARS).
        :param label_params: Optional; A list of label parameters to be checked for marker labels.
        """
        with open(filename, 'rb') as handle:
            reader = c3d.Reader(handle)

            # Set file metadata.
            self['PathFileType'] = 3
            self['DataFormat'] = "(X/Y/Z)"
            self['FileName'] = os.path.basename(filename)

            # Set file header values.
            self['DataRate'] = reader.header.frame_rate
            self['CameraRate'] = reader.header.frame_rate
            self['NumFrames'] = reader.header.last_frame - reader.header.first_frame + 1
            self['Units'] = reader.get('POINT').get('UNITS').string_value
            self['OrigDataRate'] = reader.header.frame_rate
            self['OrigDataStartFrame'] = reader.header.first_frame
            self['OrigNumFrames'] = reader.header.last_frame - reader.header.first_frame + 1

            # Set frame numbers.
            self['Frame#'] = [i for i in range(reader.header.first_frame, reader.header.last_frame + 1)]

            point_group = reader.get('POINT')
            if filter_output is None:
                filter_output = ['ANGLES', 'FORCES', 'MOMENTS', 'POWERS', 'SCALARS']
            if label_params is None:
                label_params = [key for key in point_group.param_keys() if re.fullmatch(r'LABELS\d*', key)]

            # Filter out model outputs (Angles, Forces, Moments, Powers, Scalars) from point labels.
            model_outputs = set()
            for param in filter_output:
                if param in point_group.param_keys():
                    model_outputs.update(point_group.get(param).string_array)
            point_labels = []
            for param in label_params:
                if param in point_group.param_keys():
                    filtered_labels = [None if label in model_outputs else label.strip() for label in
                                       point_group.get(param).string_array]
                    point_labels.extend(filtered_labels)

            # Set marker labels.
            self['Markers'] = [label for label in point_labels if label]
            self['NumMarkers'] = len(self['Markers'])

            # Set marker data.
            for i, points, analog in reader.read_frames():
                time = (i - 1) * (1 / reader.point_rate)
                point_data = []
                for j in range(len(points)):
                    if point_labels[j]:
                        coordinates = points[j][:3].tolist()
                        errors = points[j][3:]
                        for error in errors:
                            if error == -1:
                                coordinates = _convert_coordinates(['', '', ''])
                                break
                        point_data.append(coordinates)
                self[i] = time, point_data

    def import_from(self, filename, *args, **kwargs):
        """
        Import data from a non-TRC file source.
        Currently, the only alternative supported format is c3d. The C3D import method also
        accepts: `filter_output`, an optional argument allowing the user to specify C3D
        model-output groups that should be filtered out from the list of marker labels; and
        `label_params`, an optional list of the C3D parameters containing the marker labels.

        :param filename: The source file of the data to be imported.
        """
        self._import_from_c3d(filename, *args, **kwargs)

    def save(self, filename, add_trailing_tab=False):
        """
        Save TRC motion capture data to a file specified by filename.
        To work with OpenSIM and Mokka formats set the add trailing tab parameter to True.

        :param filename: String or pathlike to write to.
        :param add_trailing_tab: Add a trailing tab to the header and data lines [default: False].
        """
        if 'PathFileType' in self:
            header_line_1 = f"PathFileType\t{self['PathFileType']}\t{self['DataFormat']}\t{self['FileName']}{os.linesep}"
        else:
            raise NotImplementedError('Do not know this file type.')

        # Check that all known header keys are present
        for header_key in _HEADER_KEYS:
            if header_key not in self:
                raise KeyError(f'Could not find required header key: {header_key}')

        data_format_count = len(self['DataFormat'].split('/'))

        header_line_2 = '\t'.join(_HEADER_KEYS) + os.linesep
        header_line_3 = '\t'.join(
            [str(_convert_header_key_value_to_type(key, self[key])) for key in _HEADER_KEYS]) + os.linesep

        format_adjustment = '\t' if add_trailing_tab else ''

        coordinate_labels = _COORDINATE_LABELS[:data_format_count]
        markers_header = [entry for marker in self['Markers'] for entry in [marker, '', '']]
        marker_sub_heading = [f'{coordinate}{i + 1}' for i in range(len(self['Markers'])) for coordinate in
                              coordinate_labels]
        data_header_line_1 = 'Frame#\tTime\t' + '\t'.join(markers_header) + format_adjustment + os.linesep
        data_header_line_2 = '\t\t' + '\t'.join(marker_sub_heading) + format_adjustment + os.linesep

        blank_line = os.linesep

        with open(filename, 'w', newline='') as f:

            f.write(header_line_1)
            f.write(header_line_2)
            f.write(header_line_3)

            f.write(data_header_line_1)
            f.write(data_header_line_2)

            f.write(blank_line)

            for frame in self['Frame#']:
                time, line_data = self[frame]
                values = ['' if math.isnan(v) else f'{v:.5f}' for values in line_data for v in values]
                numeric_values = '\t'.join(values)
                f.write(f'{frame}\t{time:.3f}\t{numeric_values}{format_adjustment}{os.linesep}')
