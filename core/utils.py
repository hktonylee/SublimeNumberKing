
import sublime, sublime_plugin
from .settings import SELECT_TYPE_INT, SELECT_TYPE_FLOAT, SELECT_TYPE_AUTO, SELECT_TYPE_INT_NEAREST


def parse_csv_line(line):
    def parse(line):
        def reduce_list(func, lst, initial_value):
            value = initial_value
            for item in lst:
                value = func(item, value)
                yield value

        if len(line) == 0:
            yield [], 0, 0
        components = line.split(',')
        indexes = tuple(reduce_list(lambda x, v: (v[1] + 1, v[1] + len(x) + 1), components, (-1, -1)))

        quoting_start = None
        for i in range(len(components)):
            if len(components[i]) > 0:
                if components[i][0] == '"':
                    if quoting_start is None:
                        quoting_start = i
                if components[i][-1] == '"':
                    if quoting_start is not None:
                        return_str = ','.join(components[quoting_start:i+1]).strip('"')
                        yield return_str, indexes[quoting_start][0], indexes[i][1]
                        quoting_start = None
                        continue    # skip duplicate yield
            if quoting_start is None:
                yield components[i], indexes[i][0], indexes[i][1]
        # return components
        if quoting_start is not None:
            yield ','.join(components[quoting_start:]), indexes[quoting_start][0], indexes[-1][1]

    return parse(line)


def get_current_sel(sel, view):
    len_sel = len(sel)
    if len_sel == 0 or (len_sel == 1 and sel[0].empty()):
        yield sublime.Region(0, view.size())
    else:
        for region in sel:
            yield region


def to_int(s, failed, error_msg):
    try:
        n = int(s)
        if failed(n):
            raise ValueError()
        else:
            return n
    except ValueError:
        sublime.error_message(error_msg)


def to_positive_int(s):
    return to_int(s, lambda n: n < 1, 'Interlaced count must be positive integer.')


def to_non_negative_int(s):
    return to_int(s, lambda n: n < 0, 'Interlaced count must be non-negative integer.')


def get_select_regex(select_type):
    if select_type == SELECT_TYPE_INT or select_type == SELECT_TYPE_INT_NEAREST:
        return '-?\d+'
    elif select_type == SELECT_TYPE_FLOAT or select_type == SELECT_TYPE_AUTO:
        return '-?\d+(\.\d+)?'
    else:
        raise Exception('Unsupport select number select_type: ' + str(select_type))


def infer_select_type():
    return None
