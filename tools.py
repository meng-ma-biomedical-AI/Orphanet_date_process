import inspect
import sys


def retrieve_name(var):
    """
    Find the name of the object "subfunction of get_size"
    """
    for fi in reversed(inspect.stack()):
        names = [var_name for var_name, var_val in fi.frame.f_locals.items() if var_val is var]
        if len(names) > 0:
            return names[0]


class SizeObj:
    def __init__(self, ret_text, exact_size, size, round_size, unit, name):
        self.text = ret_text
        self.exact_size = exact_size
        self.size = size
        self.round_size = round_size
        self.unit = unit
        self.name = name


def get_size(obj, seen=None, level=1):
    """
    Recursively finds size of objects
        Then returns the name of the queried object and its size in kb
    """
    size = sys.getsizeof(obj)
    if seen is None:
        seen = set()
    obj_id = id(obj)
    if obj_id in seen:
        return 0
    # Important mark as seen *before* entering recursion to gracefully handle
    # self-referential objects
    seen.add(obj_id)
    if isinstance(obj, dict):
        size += sum([get_size(v, seen, level + 1) for v in obj.values()])
        size += sum([get_size(k, seen, level + 1) for k in obj.keys()])
    elif hasattr(obj, '__dict__'):
        size += get_size(obj.__dict__, seen, level + 1)
    elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes, bytearray)):
        size += sum([get_size(i, seen, level + 1) for i in obj])
    exact_size = size
    if level == 1:
        unit = "b"
        if size / 10**9 > 1:
            size /= 10**9
            unit = "gb"
        elif size / 10**6 > 1:
            size /= 10**6
            unit = "mb"
        elif size / 10**3 > 1:
            size /= 10**3
            unit = "kb"
        name = retrieve_name(obj)
        round_size = round(size, 2)
        ret_text = "{} {} for {}\n".format(round_size, unit, name)
        size_obj = SizeObj(ret_text, exact_size, size, round_size, unit, name)
        return size_obj
    return size
