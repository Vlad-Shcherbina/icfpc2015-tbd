"""
Abnormal exits (such as assertion failures in C extensions), nose, hypothesis,
coverage, and continuous testing philosophy interact with each other in weird
ways.

This collection of crutches attempts to mitigate some undesirable effects of
such interactions.
"""

import functools
import os
import sys
import selectors
import pickle
import traceback
import warnings
import logging
import inspect

import hypothesis


class AbnormalExit(Exception):
    pass


def isolate_process_failures():
    """
    Decorate test method to run in a forked process.

    This decorator relies on the assumption that return value or raised
    exception is picklable.
    stdout and stderr are forwarded (actually, stderr goes to stdout
    because nose).
    If child process exits, AbnormalExit will be raised.

    Not that if used with @hypothesis.given, given should only receive
    keyword arguments.
    """

    def decorator(f):
        # Hopefully this hack with 'self' that limits this decorator to methods
        # won't be necessary once
        # https://github.com/DRMacIver/hypothesis/issues/113 is addressed.
        assert inspect.getargspec(f).args[0] == 'self'
        @functools.wraps(f)
        def wrapped_f(self, **kwargs):
            return _run_in_a_separate_process(lambda: f(self, **kwargs))
        return wrapped_f

    return decorator


def _run_in_a_separate_process(f):
    if not _isolate:
        return f()
    if not hasattr(os, 'fork'):
        warnings.warn('os does not have fork, process isolation will not work')
        return f()

    stdout_pipe_r, stdout_pipe_w = os.pipe()
    stdout_pipe_r = os.fdopen(stdout_pipe_r)
    stdout_pipe_w = os.fdopen(stdout_pipe_w, 'w')

    stderr_pipe_r, stderr_pipe_w = os.pipe()
    stderr_pipe_r = os.fdopen(stderr_pipe_r)
    stderr_pipe_w = os.fdopen(stderr_pipe_w, 'w')

    control_pipe_r, control_pipe_w = os.pipe()
    control_pipe_r = os.fdopen(control_pipe_r, 'rb')
    control_pipe_w = os.fdopen(control_pipe_w, 'wb')

    pid = os.fork()
    if pid == 0:  # child
        stdout_pipe_r.close()
        stderr_pipe_r.close()
        control_pipe_r.close()

        os.dup2(stdout_pipe_w.fileno(), 1)
        os.dup2(stderr_pipe_w.fileno(), 2)

        # Even if nose set up stdout capture, we don't want it to happen in
        # child process
        sys.stdout = stdout_pipe_w
        # Note that nose does not capture stderr.

        # Same for log capture.
        root_logger = logging.getLogger()
        handlers = list(root_logger.handlers)
        for h in handlers:
            root_logger.removeHandler(h)
        # Because basicConfig does nothing if there are any root handlers.
        logging.basicConfig(level=logging.DEBUG)
        # TODO: Instead of logging to stderr, it is possible to send log records
        # over control pipe and reemit them in the parent.

        try:
            result = f()
        except BaseException as e:
            pickle.dump((False, e), control_pipe_w)
            # Traceback will be lost when reraising deserialized exception in
            # the parent, so we print it out here.
            traceback.print_exc()
        else:
            pickle.dump((True, result), control_pipe_w)

        stdout_pipe_w.close()
        stderr_pipe_w.close()
        control_pipe_w.close()
        os._exit(0)

    # parent

    stdout_pipe_w.close()
    stderr_pipe_w.close()
    control_pipe_w.close()

    selector = selectors.DefaultSelector()
    selector.register(stdout_pipe_r, selectors.EVENT_READ)
    selector.register(stderr_pipe_r, selectors.EVENT_READ)
    selector.register(control_pipe_r, selectors.EVENT_READ)
    remaining_selectors = 3

    control = []

    while remaining_selectors:
        events = selector.select()
        for key, mask in events:
            assert mask == selectors.EVENT_READ
            if key.fileobj is stdout_pipe_r:
                x = stdout_pipe_r.read(1024)
                if x:
                    sys.stdout.write(x)
                else:
                    selector.unregister(stdout_pipe_r)
                    remaining_selectors -= 1
            elif key.fileobj is stderr_pipe_r:
                x = stderr_pipe_r.read(1024)
                if x:
                    sys.stdout.write(x)
                    # That's right, write to stdout, to work around nose not
                    # capturing stderr.

                    # TODO: Currently it is possible for stdout and stderr
                    # to mix up. Perhaps it is not that hard to keep them on
                    # separate lines.
                    # Also perhaps this whole business of redirecting stderr to
                    # stdout should be factored out into a separate decorator.
                else:
                    selector.unregister(stderr_pipe_r)
                    remaining_selectors -= 1
            elif key.fileobj is control_pipe_r:
                x = control_pipe_r.read(1024)
                if x:
                    control.append(x)
                else:
                    selector.unregister(control_pipe_r)
                    remaining_selectors -= 1
            else:
                assert False, key.fileobj

    _, exit_status = os.waitpid(pid, 0)
    if exit_status != 0:
        raise AbnormalExit(exit_status)

    control = b''.join(control)
    success, data = pickle.loads(control)

    if success:
        return data
    else:
        raise data


_isolate = True


def disable_isolation():
    """
    For coverage runs (because combining coverage data from child processes
    is extra work) or simply to speed up tests.
    """
    global _isolate
    _isolate = False


def make_hypothesis_reproducible():
    # This is a workaround until
    # https://github.com/DRMacIver/hypothesis/issues/111 is fixed.
    hypothesis.Settings.default = hypothesis.Settings(database=None)
    #hypothesis.Settings.default.database_file = None

    hypothesis.Settings.default.timeout = -1
    hypothesis.Settings.default.derandomize = True
