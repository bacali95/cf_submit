import json
import os
import random
import string
from json import JSONDecodeError


class Obj(object):
    def __init__(self, d):
        for a, b in d.items():
            if isinstance(b, (list, tuple)):
                setattr(self, a, [Obj(x) if isinstance(
                    x, dict) else x for x in b])
            else:
                setattr(self, a, Obj(b) if isinstance(b, dict) else b)

    def toString(self):
        return json.dumps(self, default=lambda x: x.__dict__, indent=2)


def obj_to_dict(obj):
    if isinstance(obj, (list, tuple)):
        return [obj_to_dict(o) for o in obj]
    elif isinstance(obj, Obj):
        res = dict()
        for key, value in obj.__dict__.items():
            res[key] = obj_to_dict(value)
        return res
    else:
        return obj


def write_data_to_file(data, file_name):
    try:
        with open(file_name, 'w') as file:
            json.dump(data, file, indent=2)
            return True
    except (TypeError, OSError):
        return False


def read_data_from_file(file_name):
    try:
        if os.path.isfile(file_name):
            with open(file_name, 'r') as file:
                return json.load(file)
        else:
            return None
    except (JSONDecodeError, OSError):
        return None


def random_digits_string(length=10):
    return ''.join(random.choice(string.digits) for _ in range(length))


def safe_list_get(list_, index, default=None):
    try:
        return list_[index]
    except IndexError:
        return default
