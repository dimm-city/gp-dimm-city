"""numpy's real 2-D FFTs, spread over the CPU's cores, for the wall scripts.

np.fft runs on one core. A 2-D transform is a 1-D transform of every row and
then of every column, and numpy transforms each line on its own, so dealing
blocks of lines out to threads (numpy lets go of the GIL while it works) gives
the same numbers, to the bit, as np.fft.rfft2 and np.fft.irfft2, sooner.
"""
import os
from concurrent.futures import ThreadPoolExecutor

import numpy as np

THREADS = os.cpu_count() or 1
_pool = ThreadPoolExecutor(THREADS)


def _lines(f, a, axis, out, **kw):
    """out = f(a, axis=axis, **kw) for a 2-D a, its lines along `axis` dealt out to the threads in blocks."""
    cuts = np.linspace(0, a.shape[1 - axis], THREADS + 1).astype(int)

    def block(i, j):
        s = (slice(None), slice(i, j)) if axis == 0 else (slice(i, j),)
        f(a[s], axis=axis, out=out[s], **kw)

    list(_pool.map(block, cuts[:-1], cuts[1:]))
    return out


def rfft2(a):
    """np.fft.rfft2(a) for a real (float32 or float64) 2-D a."""
    h, w = a.shape
    rows = _lines(np.fft.rfft, a, 1, np.empty((h, w // 2 + 1), np.result_type(a.dtype, np.complex64)))
    return _lines(np.fft.fft, rows, 0, np.empty_like(rows))


def irfft2(spec, s):
    """np.fft.irfft2(spec, s=s), where spec has s[0] rows."""
    cols = _lines(np.fft.ifft, spec, 0, np.empty_like(spec))
    return _lines(np.fft.irfft, cols, 1, np.empty(s, cols.real.dtype), n=s[1])


def fft2(a):
    """np.fft.fft2(a) for a 2-D a."""
    rows = _lines(np.fft.fft, a, 1, np.empty(a.shape, np.result_type(a.dtype, np.complex64)))
    return _lines(np.fft.fft, rows, 0, np.empty_like(rows))


def ifft2(spec):
    """np.fft.ifft2(spec)."""
    rows = _lines(np.fft.ifft, spec, 1, np.empty_like(spec))
    return _lines(np.fft.ifft, rows, 0, np.empty_like(rows))
