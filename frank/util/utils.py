
import math


def is_numeric(val):
    if isinstance(val, int) or isinstance(val, float):
        return True
    else:
        try:
            return isinstance(float(val), float)
        except:
            return False


def get_number(val, default):
    return float(val) if is_numeric(val) else default


def to_precision(x, p):
    """
    Reference: http://randlet.com/blog/python-significant-figures-format/
    returns a string representation of x formatted with a precision of p

    Based on the webkit javascript implementation taken from here:
    https://code.google.com/p/webkit-mirror/source/browse/JavaScriptCore/kjs/number_object.cpp
    """

    x = float(x)

    if x == 0.:
        return "0." + "0"*(p-1)

    out = []

    if x < 0:
        out.append("-")
        x = -x

    e = int(math.log10(x))
    tens = math.pow(10, e - p + 1)
    n = math.floor(x/tens)

    if n < math.pow(10, p - 1):
        e = e - 1
        tens = math.pow(10, e - p+1)
        n = math.floor(x / tens)

    if abs((n + 1.) * tens - x) <= abs(n * tens - x):
        n = n + 1

    if n >= math.pow(10, p):
        n = n / 10.
        e = e + 1

    m = "%.*g" % (p, n)

    if e < -2 or e >= p:
        out.append(m[0])
        if p > 1:
            out.append(".")
            out.extend(m[1:p])
        out.append('e')
        if e > 0:
            out.append("+")
        out.append(str(e))
    elif e == (p - 1):
        out.append(m)
    elif e >= 0:
        out.append(m[:e+1])
        if e+1 < len(m):
            out.append(".")
            out.extend(m[e+1:])
    else:
        out.append("0.")
        out.extend(["0"]*-(e+1))
        out.append(m)

    return float("".join(out)) if '.' in out else int("".join(out))


def listify(possible_list):
    if not isinstance(possible_list, list):
        return [possible_list]

    return possible_list


def filter_out_falsy(a_list_of_possible_falsy_things):
    return list(filter(lambda x: x, a_list_of_possible_falsy_things))
