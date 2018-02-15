import logging
from time import time


logger = logging.getLogger('performance')


def func_time(func):
    def wrap(*args, **kwargs):
        t = time()
        result = func(*args, **kwargs)
        logger.warning("[{1:.3f}] {0}".format(func.__name__, time() - t))
        return result

    return wrap
