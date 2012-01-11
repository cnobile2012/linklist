import os, sys

__version__ = "2.0.0"

from setuptools import setup, find_packages
from distutils.extension import Extension

ext_modules = [
    Extension("dlinklist.libdll", ["src/dll_main.c"])
    ]

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name='DLinklist',
      version=__version__,
      description="Python wrapper for the Doubly Linked List C API.",
      long_description=read('README'),
      keywords="DLL doubly linked list linklist python API",
      author='Carl J. Nobile',
      author_email='carl.nobile@gmail.com',
      url='wiki.tetrasys-design.net',
      license='Artistic and Eclipse',
      package_dir={'': 'src'},
      py_modules=['dlinklist.__init__', 'dlinklist.linklist',],
      data_files=[('dlinklist/test',
                   ['test/ll_test.py',],),
                 ],
      ext_modules=ext_modules,
      zip_safe=False
      )
