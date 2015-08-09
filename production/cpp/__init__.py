# Magically compile extension in this package when we try to import it.

import sys
import os

# Not `from distutils.core import setup`, otherwise nose will attempt to run
# `setup` function.
import distutils.core

def setup():
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


class RedirectStdoutToStderr(object):
    def __enter__(self):
        sys.stdout.flush()
        self.old_stdout = sys.stdout
        sys.stdout = sys.stderr

    def __exit__(self, exc_type, exc_value, traceback):
        sys.stdout.flush()
        sys.stdout = self.old_stdout


# Make sure everything goes to stderr otherwise we risk to pollute to output of
# the solver and corrupt the solution.
with RedirectStdoutToStderr():
    setup()
