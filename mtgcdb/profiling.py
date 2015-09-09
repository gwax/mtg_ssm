"""Profiling code."""

from __future__ import print_function

import cProfile
import pstats
import contextlib

import six


def start():
    """Start and return profiler."""
    profiler = cProfile.Profile()
    profiler.enable()
    return profiler


def finish(profiler):
    """Stop the profiler and print out stats."""
    profiler.disable()
    out_stream = six.StringIO()
    profile_stats = pstats.Stats(
        profiler, stream=out_stream).sort_stats('cumulative')
    profile_stats.print_stats(30)
    print(out_stream.getvalue())


@contextlib.contextmanager
def profiled():
    profiler = start()
    yield
    finish(profiler)
