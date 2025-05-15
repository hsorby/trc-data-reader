
TRC Data Reader
===============

.. image:: https://img.shields.io/badge/license-Apache%202-yellow
  :target: https://opensource.org/licenses/Apache-2.0

.. image:: https://badge.fury.io/py/trc-data-reader.svg
  :target: https://pypi.org/project/trc-data-reader/

.. image:: https://github.com/hsorby/trc-data-reader/workflows/trc-data-reader/badge.svg
  :target: https://pypi.org/project/trc-data-reader/

.. image:: https://raw.githubusercontent.com/hsorby/badges/main/trc-data-reader/coverage.svg
  :target: https://pypi.org/project/trc-data-reader/

Python package for reading track row column (TRC) motion capture data.
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
