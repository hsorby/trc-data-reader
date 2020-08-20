
TRC Data Reader
===============

Python package for reading trc motion capture data.
TRC data reader captures the motion capture data and puts it into a dict like object.

TRC data reader can read motion capture data from file or from a multi-line string.

For a valid trc file or multi-line data string the following keys will be present (among others):

- FileName
- DataFormat
- Markers
- DataRate
- NumFrames
- NumMarkers

Usage
-----

::
 from trc import TRCData

 mocap_data = TRCData()
 mocap_data.load('/path/to/file/')

 num_frames = mocap_data['NumFrames']
