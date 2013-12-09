import random

def is_int(val, tolerance=6):
    try:
        int_ = int(val)
        float_ = float(round(val, tolerance))
    except:
        return False
    if int_ == float_:
        return True
    else:
        return float_ / int(float_) == 1

def lsb_magnitude(flt):
    flt_str = str(flt)
    for index, digit in enumerate(flt_str):
        if digit == '.':
            return len(flt_str[index + 1:])
    return 0

def step_range(start, end, step):
    """
    Returns range between start and end, by step, inclusive
    >>> step_range(.25, .15, .05)
    []
    >>> step_range(.15, .15, .05)
    [0.15]
    >>> step_range(.15, .25, .05)
    [0.15, 0.2, 0.25]
    >>> step_range(0, 1, .1)
    [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    >>> step_range(.2, .25, .02)
    Traceback (most recent call last):
        ...
    ValueError: Step does not evenly divide the range given.
    """
    if start > end:
        return []

    steps = (end - start) / step + 1
    if not is_int(steps):
        raise ValueError("Step does not evenly divide the range given.")
    else:
        steps = int(steps)

    return map(lambda i: round(start + (i * step), 5), range(0, steps))

def percent_sample(collection, percent):
    """
    Returns a random sample of size |collection| * percent
    >>> len(percent_sample([0,1,2,3], 0))
    0
    >>> len(percent_sample([0,1,2,3], .2))
    0
    >>> len(percent_sample([0,1,2,3], .25))
    1
    >>> len(percent_sample([0,1,2,3], .5))
    2
    >>> len(percent_sample([0,1,2,3], .75))
    3
    >>> len(percent_sample([0,1,2,3], 1))
    4
    """
    if percent < 0:
        raise ValueError("Percentage is < 0")
    elif percent > 1:
        raise ValueError("Percentage is > 1")
    return random.sample(collection,
                         int(len(collection) * percent))


if __name__ == "__main__":
    import doctest
    doctest.testmod()