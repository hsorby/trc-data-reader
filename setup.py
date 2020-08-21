from os import path
from setuptools import setup

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='trc-data-reader',
    version='0.1.3-alpha1',
    package_dir={'': 'src'},
    url='https://github.com/hsorby/trc-data-reader',
    license='Apache 2.0',
    author='Hugh Sorby',
    author_email='h.sorby@auckland.ac.nz',
    description='A package for reading trc motion capture data.',
    long_description=long_description,
    long_description_content_type='text/x-rst'
)
