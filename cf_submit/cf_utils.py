import json
import os
import random
import string


class obj(object):
    def __init__(self, d):
        for a, b in d.items():
            if isinstance(b, (list, tuple)):
                setattr(self, a, [obj(x) if isinstance(
                    x, dict) else x for x in b])
            else:
                setattr(self, a, obj(b)
                        if isinstance(b, dict) else b)

    def toString(self):
        return json.dumps(self, default=lambda x: x.__dict__, indent=2)


def writeDataToFile(data, file_name):
    if file_name:
        with open(file_name, 'w') as file:
            if isinstance(data, dict):
                json.dump(data, file, indent=2)
            elif isinstance(data, (list, tuple)):
                json.dump([d.__dict__ for d in data], file, indent=2)
            else:
                json.dump(data.__dict__, file, indent=2)
            return True
    return False


def readDataFromFile(file_name):
    if file_name and os.path.isfile(file_name):
        with open(file_name, 'r') as file:
            return json.load(file)
    return None


def randomDigitsString(stringLength=10):
    letters = string.digits
    return ''.join(random.choice(letters) for i in range(stringLength))


def safeListGet(list_, index, default=None):
    try:
        return list_[index]
    except IndexError:
        return default
