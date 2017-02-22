import time
import random


def func_time(func):
    def wrap(*args, **kwargs):
        t = time.time()
        result = func(*args, **kwargs)
        print("{}: {}".format(func.__name__, round(time.time() - t, 4)))
        return result

    return wrap


@func_time
def f(arr):
    result = list()
    arr.sort()

    for i, l in enumerate(arr[1:], 1):
        if arr[i-1] == l and l not in result:
            result.append(l)
    return result


@func_time
def f2(arr):
    result = []
    for x in arr:
        if arr.count(x) > 1 and x not in result:
            result.append(x)
    return result


for c in (1000, 10*1000, 20*1000):
    print(c)
    d = [random.randint(1, c) for a in range(c)]
    dd = d[:]
    p = f(d)
    pp = f2(dd)

    print(set(p) == set(pp))
