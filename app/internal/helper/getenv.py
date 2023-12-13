import os


def env(variable, default=None):
    val = os.environ.get(variable)
    return val if val not in (None, "") else default
