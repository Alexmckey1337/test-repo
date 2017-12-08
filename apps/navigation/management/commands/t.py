import random

import time


def func_time(func):
    def wrap(*args, **kwargs):
        t = time.time()
        result = func(*args, **kwargs)
        print("{}: {}".format(func.__name__, round(time.time() - t, 4)))
        return result

    return wrap


@func_time
def f3(arr):
    res = list()
    other = set()
    for l in arr:
        if l in other and l not in res:
            res.append(l)
        other.add(l)
    return res


@func_time
def f(arr):
    res = set()
    arr.sort()
    for i, l in enumerate(arr[1:], 1):
        if arr[i - 1] == l:
            res.add(l)
    return list(res)


@func_time
def f5(arr):
    res = list()
    arr.sort()
    for i, l in enumerate(arr[1:], 1):
        if arr[i - 1] == l and l not in res:
            res.append(l)
    return list(res)


@func_time
def f4(arr):
    res, other = set(), set()
    for l in arr:
        if l in other:
            res.add(l)
        other.add(l)
    return list(res)


c = 1000 * 1000

tes = [random.randint(1, c) for _ in range(c)]
f4(tes)
