
# TRC Data Reader


[![License](https://img.shields.io/badge/license-Apache%202-yellow)](https://opensource.org/licenses/Apache-2.0)
[![PyPI version](https://badge.fury.io/py/trc-data-reader.svg)](https://pypi.org/project/trc-data-reader/)
[![Build Status](https://github.com/hsorby/trc-data-reader/workflows/trc-data-reader/badge.svg)](https://pypi.org/project/trc-data-reader/)
[![Coverage](https://raw.githubusercontent.com/hsorby/badges/main/trc-data-reader/coverage.svg)](https://pypi.org/project/trc-data-reader/)

A lightweight, dependency-free Python package for reading, processing, and writing track row column (TRC) motion capture data.

The `TRCData` object behaves like a standard Python dictionary, providing simple, direct access to all header metadata and time-series marker data.

## Installation

```bash
pip install trc-data-reader
```

## Usage

The `TRCData` object is the main entry point.

```python
from trc import TRCData

# Create an instance.
mocap_data = TRCData()
```

### 1. Loading Data

You can load data from a TRC file, a C3D file, or parse it directly from a string.

Load from a .trc file:

```python
mocap_data.load('path/to/my_data.trc')
```

Load from a .c3d file:

```python
# Requires the 'c3d' package to be installed (pip install c3d)
mocap_data.import_from('path/to/my_data.c3d')
```

Parse from a multi-line string:

```python
data_string = """PathFileType	4	(X/Y/Z)	filename.trc
DataRate	CameraRate	NumFrames	NumMarkers	Units	OrigDataRate	OrigDataStartFrame	OrigNumFrames
60.0	60.0	2	1	mm	60.0	1	2
Frame#	Time	Marker1
		X1	Y1	Z1
1	0.000	1.0	2.0	3.0
2	0.017	1.1	2.1	3.1
"""
mocap_data.parse(data_string)
```

### 2. Accessing Data

The object works like a dictionary. Header metadata is stored as top-level keys, as is marker data.

#### Accessing Header Metadata:

```python
print(f"File: {mocap_data['FileName']}")
print(f"Total Frames: {mocap_data['NumFrames']}")
print(f"Data Rate: {mocap_data['DataRate']} Hz")
print(f"Available Markers: {mocap_data['Markers']}")
```

#### Accessing Marker Data (Time-Series):

This is the most common use case. Accessing a marker by its name gives you its complete time-series data.

```python
# Get all [X, Y, Z] coordinates for the 'Marker1'
marker_data = mocap_data['Marker1']

# Get the coordinates for the first frame (index 0)
print(marker_data[0])
# Output: [1.0, 2.0, 3.0]

# Get the coordinates for the second frame (index 1)
print(marker_data[1])
# Output: [1.1, 2.1, 3.1]
```

#### Accessing Data by Frame:

You can also access all data for a specific frame by using the frame number as the key.

```python
# Get all data for Frame 1
frame, (time, marker_list) = 1, mocap_data[1]

print(f"Frame: {frame}")
print(f"Time: {time}")
print(f"All Marker Coords: {marker_list}")
# Output:
# Frame: 1
# Time: 0.0
# All Marker Coords: [[1.0, 2.0, 3.0]]
```

### 3. Saving Data

You can save the loaded (or modified) data back to a TRC file.

```python
# ...after loading or modifying data
mocap_data.save('path/to/output_file.trc')
```

## Developing

To install for development, clone the repository and install in editable mode with test dependencies:

```bash
git clone https://github.com/hsorby/trc-data-reader.git
cd trc-data-reader
pip install -e ".[test]"
```

Run tests from the root directory:

```bash
python -m unittest discover -s tests
```

Run coverage analysis, from the same directory:

```bash
coverage run --source src -m unittest discover
coverage report -m
```

This library aims for 100% coverage of its lines of code.
