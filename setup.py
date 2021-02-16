
import os
from setuptools import setup


basedir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(basedir, 'VERSION'), 'r') as _f:
    __version__ = _f.read().strip()


setup(
    name='helmholtz',
    version=__version__,
    description='Helmholtz coil control application',
    url='https://github.com/lnls-ima/helmholtz-coil-control',
    author='lnls-ima',
    license='MIT License',
    packages=['helmholtz'],
    install_requires=[
        'pyvisa',
        'numpy',
        'scipy',
        'pandas',
        'pyqtgraph',
        'pyserial',
        'qtpy',
        'openpyxl',
    ],
    test_suite='nose.collector',
    tests_require=['nose'],
    zip_safe=False)