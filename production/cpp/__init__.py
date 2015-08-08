# Magically compile extension in this package when we try to import it.

import sys
import os

# Not `from distutils.core import setup`, otherwise nose will attempt to run
# `setup` function.
import distutils.core


cur_dir = os.getcwd()
try:
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    distutils.core.setup(
        name='placement',
        py_modules=['placement'],
        ext_modules=[
            distutils.core.Extension('_placement',
                ['placement.i', 'placement.cpp'],
                depends=['placement.h'],
                swig_opts=['-c++'],
                extra_compile_args=['-std=c++11'],
                undef_macros=['NDEBUG'],  # want assertions
            ),
        ],
        script_args=['build_ext', '--inplace']
    )
finally:
    os.chdir(cur_dir)
