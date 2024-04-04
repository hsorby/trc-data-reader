import os
import c3d


_REQUIRED_HEADER_KEYS = ['DataRate', 'CameraRate', 'NumFrames', 'NumMarkers', 'Units', 'OrigDataRate']
_HEADER_KEYS = ['DataRate', 'CameraRate', 'NumFrames', 'NumMarkers', 'Units', 'OrigDataRate', 'OrigDataStartFrame', 'OrigNumFrames']
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

    def _process_contents(self, contents):
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
                sections = line.split('\t')
                if len(sections) != 4:
                    raise IOError('File format invalid: Header line 1 does not start have four sections.')
                self[sections[0]] = sections[1]
                self['DataFormat'] = sections[2]
                data_format_count = len(sections[2].split('/'))
                self['FileName'] = sections[3]
            elif current_line_number == 2:
                # File Header 2
                file_header_keys = line.split('\t')
            elif current_line_number == 3:
                # File Header 3
                file_header_data = line.split('\t')
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
                data_header_markers = line.split('\t')
                if data_header_markers[0] != 'Frame#':
                    raise IOError('File format invalid: Data header does not start with "Frame#".')
                if data_header_markers[1] != 'Time':
                    raise IOError('File format invalid: Data header in position 2 is not "Time".')

                self['Frame#'] = []
                self['Time'] = []
            elif current_line_number == 5:
                # Data Header 1
                data_header_sub_marker = line.split('\t')
                if len(data_header_markers) != len(data_header_sub_marker):
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
                    sections = line.split('\t')

                    try:
                        frame = int(sections.pop(0))
                        self['Frame#'].append(frame)
                    except ValueError:
                        if int(self['NumFrames']) == len(self['Frame#']):
                            # We have reached the end of the specified frames
                            continue
                        else:
                            raise IOError(
                                f"File format invalid: Data frame {len(self['Frame#'])} is not valid.")

                    time = float(sections.pop(0))
                    self['Time'].append(time)

                    line_data = [[float('nan')] * data_format_count] * int(self['NumMarkers'])
                    len_section = len(sections)
                    expected_entries = len(line_data) * data_format_count
                    if len_section > expected_entries:
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

    def parse(self, data):
        """
        Parse trc formatted motion capture data into a dictionary like object.

        :param data: The multi-line string of the data to parse.
        """
        contents = data.split('\n')
        self._process_contents(contents)

    def load(self, filename):
        """
        Load a trc motion capture data file into a dictionary like object.

        :param filename: The name of the file to load.
        """
        with open(filename, 'rb') as f:
            contents = f.read().decode()

        contents = contents.split(os.linesep)
        self._process_contents(contents)

    def _import_from_c3d(self, filename):
        """
        Extracts TRC data from a C3D file.

        :param filename: The C3D file to be parsed.
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
            self['NumFrames'] = reader.header.last_frame
            self['NumMarkers'] = reader.get('POINT').get('USED').int16_value
            self['Units'] = reader.get('POINT').get('UNITS').string_value
            self['OrigDataRate'] = reader.header.frame_rate
            self['OrigDataStartFrame'] = reader.header.first_frame
            self['OrigNumFrames'] = reader.header.last_frame

            # Set data column labels.
            self['Markers'] = [label.strip() for label in reader.point_labels]

            # Set frame numbers.
            self['Frame#'] = [i for i in range(1, self['NumFrames'] + 1)]

            # Set marker data.
            for i, points, analog in reader.read_frames():
                time = (i - 1) * (1 / reader.point_rate)
                self[i] = time, [point[:3].tolist() for point in points]

    def import_from(self, filename):
        """
        Import data from a non-TRC file source.
        Currently, the only alternative supported format is c3d.

        :param filename: The source file of the data to be imported.
        """
        self._import_from_c3d(filename)

    def save(self, filename):
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
        header_line_3 = '\t'.join([str(_convert_header_key_value_to_type(key, self[key])) for key in _HEADER_KEYS]) + os.linesep

        coordinate_labels = _COORDINATE_LABELS[:data_format_count]
        markers_header = [entry for marker in self['Markers'] for entry in [marker, '', '']]
        marker_sub_heading = [f'{coordinate}{i + 1}' for i in range(len(self['Markers'])) for coordinate in coordinate_labels]
        data_header_line_1 = 'Frame#\tTime\t' + '\t'.join(markers_header).strip() + os.linesep
        data_header_line_2 = '\t\t' + '\t'.join(marker_sub_heading) + os.linesep

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
                values = [f'{v:.5f}' for values in line_data for v in values]
                numeric_values = '\t'.join(values)
                f.write(f'{frame}\t{time:.3f}\t{numeric_values}{os.linesep}')


# #!/usr/bin/env python
# '''This creates an app to launch a python script. The app is
# created in the directory where python is called. A version of Python
# is created via a softlink, named to match the app, which means that
# the name of the app rather than Python shows up as the name in the
# menu bar, etc, but this requires locating an app version of Python
# (expected name .../Resources/Python.app/Contents/MacOS/Python in
# directory tree of calling python interpreter).
#
# Run this script with one or two arguments:
#     <python script>
#     <project name>
# The script path may be specified relative to the current path or given
# an absolute path, but will be accessed via an absolute path. If the
# project name is not specified, it will be taken from the root name of
# the script.
# '''
# import sys, os, os.path, stat
# def Usage():
#     print("\n\tUsage: python "+sys.argv[0]+" <python script> [<project name>]\n")
#     sys.exit()
#
# version = "1.0.0"
# bundleIdentifier = "org.test.test"
#
# if not 2 <= len(sys.argv) <= 3:
#     Usage()
#
# script = os.path.abspath(sys.argv[1])
# if not os.path.exists(script):
#     print("\nFile "+script+" not found")
#     Usage()
# if os.path.splitext(script)[1].lower() != '.py':
#     print("\nScript "+script+" does not have extension .py")
#     Usage()
#
# if len(sys.argv) == 3:
#     project = sys.argv[2]
# else:
#     project = os.path.splitext(os.path.split(script)[1])[0]
#
# # find the python application; must be an OS X app
# pythonpath,top = os.path.split(os.path.realpath(sys.executable))
# while top:
#     if 'Resources' in pythonpath:
#         pass
#     elif os.path.exists(os.path.join(pythonpath,'Resources')):
#         break
#     pythonpath,top = os.path.split(pythonpath)
# else:
#     print("\nSorry, failed to find a Resources directory associated with "+str(sys.executable))
#     sys.exit()
# pythonapp = os.path.join(pythonpath,'Resources','Python.app','Contents','MacOS','Python')
# if not os.path.exists(pythonapp):
#     print("\nSorry, failed to find a Python app in "+str(pythonapp))
#     sys.exit()
#
# apppath = os.path.abspath(os.path.join('.',project+".app"))
# newpython =  os.path.join(apppath,"Contents","MacOS",project)
# projectversion = project + " " + version
# if os.path.exists(apppath):
#     print("\nSorry, an app named "+project+" exists in this location ("+str(apppath)+")")
#     sys.exit()
#
# os.makedirs(os.path.join(apppath,"Contents","MacOS"))
#
# f = open(os.path.join(apppath,"Contents","Info.plist"), "w")
# f.write('''<?xml version="1.0" encoding="UTF-8"?>
# <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
# <plist version="1.0">
# <dict>
#     <key>CFBundleDevelopmentRegion</key>
#     <string>English</string>
#     <key>CFBundleExecutable</key>
#     <string>main.sh</string>
#     <key>CFBundleGetInfoString</key>
#     <string>{:}</string>
#     <key>CFBundleIconFile</key>
#     <string>app.icns</string>
#     <key>CFBundleIdentifier</key>
#     <string>{:}</string>
#     <key>CFBundleInfoDictionaryVersion</key>
#     <string>6.0</string>
#     <key>CFBundleName</key>
#     <string>{:}</string>
#     <key>CFBundlePackageType</key>
#     <string>APPL</string>
#     <key>CFBundleShortVersionString</key>
#     <string>{:}</string>
#     <key>CFBundleSignature</key>
#     <string>????</string>
#     <key>CFBundleVersion</key>
#     <string>{:}</string>
#     <key>NSAppleScriptEnabled</key>
#     <string>YES</string>
#     <key>NSMainNibFile</key>
#     <string>MainMenu</string>
#     <key>NSPrincipalClass</key>
#     <string>NSApplication</string>
# </dict>
# </plist>
# '''.format(projectversion, bundleIdentifier, project, projectversion, version)
#     )
# f.close()
#
# # not sure what this file does
# f = open(os.path.join(apppath,'Contents','PkgInfo'), "w")
# f.write("APPL????")
# f.close()
# # create a link to the python app, but named to match the project
# os.symlink(pythonapp,newpython)
# # create a script that launches python with the requested app
# shell = os.path.join(apppath,"Contents","MacOS","main.sh")
# # create a short shell script
# f = open(shell, "w")
# f.write('#!/bin/sh\nexec "'+newpython+'" "'+script+'"\n')
# f.close()
# os.chmod(shell, os.stat(shell).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
