import os


def get_env(variable, default=None):
    val = os.environ.get(variable)
    return val if val != None or val != "" else default
