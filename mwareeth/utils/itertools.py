from itertools import tee, compress
from operator import not_


def partition(pred, iterable):
    """
    Returns a 2-tuple of iterables derived from the input iterable.
    The first yields the items that failed the predicate, and the second those that passed.
    """
    if pred is None:
        pred = bool

    t1, t2, p = tee(iterable, 3)
    p1, p2 = tee(map(pred, p))
    return (compress(t1, map(not_, p1)), compress(t2, p2))
