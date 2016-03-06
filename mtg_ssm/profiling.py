"""Profiling code."""

import cProfile
import io
import pstats
import contextlib


def start():
    """Start and return profiler."""
    profiler = cProfile.Profile()
    profiler.enable()
    return profiler


def finish(profiler):
    """Stop the profiler and print out stats."""
    profiler.disable()
    out_stream = io.StringIO()
    profile_stats = pstats.Stats(
        profiler, stream=out_stream).sort_stats('cumulative')
    profile_stats.print_stats(30)
    print(out_stream.getvalue())


@contextlib.contextmanager
def profiled(enabled):
    """Context manager to profile within a given context."""
    profiler = None
    if enabled:
        profiler = start()
    try:
        yield
    finally:
        if profiler is not None:
            finish(profiler)
