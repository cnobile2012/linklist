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
      keywords="DLL doubly linked list linklist python  C API",
      author='Carl J. Nobile',
      author_email='carl.nobile@gmail.com',
      maintainer='Carl J. Nobile',
      maintainer_email='carl.nobile@gmail.com',
      url='http://tetrasys-design.net/home/Linklist/index.html',
      license='Artistic and Eclipse',
      classifiers=[
          "Intended Audience :: Developers",
          "License :: OSI Approved :: Artistic License",
          "Natural Language :: English",
          "Programming Language :: C",
          "Programming Language :: Python :: 2.7",
          "Topic :: Software Development :: Libraries :: Python Modules",
          ],
      download_url="http://tetrasys-design.net/download/Linklist/dlinklist-2.0.0.tar.gz",
      platforms=["Linux", "UNIX",],
      package_dir={'': 'src'},
      py_modules=['dlinklist.__init__', 'dlinklist.linklist',],
      data_files=[('dlinklist/test',
                   ['test/ll_test.py',],),
                 ],
      ext_modules=ext_modules,
      zip_safe=False
      )
