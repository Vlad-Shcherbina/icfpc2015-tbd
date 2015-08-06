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
        name='cpp_misc',
        py_modules=['cpp_misc'],
        ext_modules=[
            distutils.core.Extension('_cpp_misc',
                ['cpp_misc.i', 'cpp_misc.cpp'],
                depends=['cpp_misc.h'],
                swig_opts=['-c++'],
                extra_compile_args=['-std=c++11'],
                undef_macros=['NDEBUG'],  # want assertions
            ),
        ],
        script_args=['build_ext', '--inplace']
    )
finally:
    os.chdir(cur_dir)
