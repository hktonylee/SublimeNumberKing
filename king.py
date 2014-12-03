import sublime, sublime_plugin
from ast import NodeTransformer, Load, Num, Call, Name, Attribute, copy_location, parse, dump
import os
from itertools import islice


class Settings:
    def __init__(self):
        self.__settings = sublime.load_settings('Number King.sublime-settings')

    def load_select_type(self):
        return self.__settings.get('SelectType') or 'float'

    def switch_select_type(self):
        current = self.load_select_type()
        current = 'int' if current == 'float' else 'float'
        self.__settings.set('SelectType', current)
        return current

    def load_last_used_formula(self):
        return self.__settings.get('LastUsedFormula') or 'x'

    def set_last_used_formula(self, formula):
        self.__settings.set('LastUsedFormula', formula)

    def load_last_used_selection_predicate(self):
        return self.__settings.get('LastUsedSelectionPredicate') or 'x > 3'

    def set_last_used_selection_predicate(self, formula):
        self.__settings.set('LastUsedSelectionPredicate', formula)


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

# print(parse_csv_line('hi'))
# print(parse_csv_line('"hi,"hihi,hi","h",bye,"hi ,hi"'))

def get_current_sel(sel, view):
    len_sel = len(sel)
    if len_sel == 0 or (len_sel == 1 and len_sel[0].empty()):
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


settings = Settings()

class Calculator(object):
    class CalculatorTransformer(NodeTransformer):
        def visit_Name(self, node):
            accepted_nodes = {'x', 'i'}
            accepted_nodes |= {'ceil', 'copysign', 'fabs', 'factorial', 'floor', 'fmod', 'frexp', 'fsum', 'isfinite', 'isinf', 'isnan', 'ldexp', 'modf', 'trunc', 'exp', 'expm1', 'log', 'log1p', 'log2', 'log10', 'pow', 'pow', 'sqrt', 'acos', 'asin', 'atan', 'atan2', 'cos', 'hypot', 'sin', 'tan', 'degrees', 'radians', 'acosh', 'asinh', 'atanh', 'cosh', 'sinh', 'tanh', 'erf', 'erfc', 'gamma', 'lgamma', 'pi', 'e'}
            if node.id in accepted_nodes:
                return node
            else:
                return None # block all other strange identifier

    def __init__(self, formula):
        self.formula = formula
        tree = parse(self.formula, '<string>', 'eval')
        tree = Calculator.CalculatorTransformer().visit(tree)
        self.code = compile(tree, '<ast_tree>', 'eval')
        import math
        self.ns = vars(math).copy()
        self.ns['__builtins__'] = None

    def calculate(self, **kwargs):
        for key, value in kwargs.items():
            self.ns[key] = value
        return eval(self.code, self.ns)


class KingNeedHelpCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        path = os.path.join(sublime.packages_path(), 'Number King', 'HELP.md')
        self.view.window().open_file(path)


class KingSwitchNumberTypeCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        select_type = settings.switch_select_type()
        sublime.status_message('Number type is switched to: ' + select_type)


def get_select_regex(select_type):
    if select_type == 'int':
        return '-?\d+'
    elif select_type == 'float':
        return '-?\d+(\.\d+)?'
    else:
        raise Exception('Unsupport select number select_type: ' + str(select_type))

class KingSelectNumberCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        select_type = settings.load_select_type()
        pattern = get_select_regex(select_type)

        current_sel = self.view.sel()
        all_regions = []
        for sel in current_sel:
            region = self.view.find(pattern, sel.begin())
            all_regions.append(region)

        current_sel.clear()
        current_sel.add_all(all_regions)


class KingInterlacedSelectCommand(sublime_plugin.TextCommand):
    def onDone(self, text):
        count = to_positive_int(text)
        
        current_sel = self.view.sel()
        all_regions = []
        i = 0
        count += 1
        for region in current_sel:
            if i % count == 0:
                all_regions.append(region)
            i += 1

        current_sel.clear()
        current_sel.add_all(all_regions)

    def askInterlacedCount(self):
        self.view.window().show_input_panel('Please the interlaced count', '', self.onDone, None, None)

    def run(self, edit):
        self.askInterlacedCount()


class KingSelectAllNumbersCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        select_type = settings.load_select_type()
        pattern = get_select_regex(select_type)

        current_sel = self.view.sel()
        all_regions = self.view.find_all(pattern)
        if len(current_sel) > 1 or not current_sel[0].empty():
            all_regions = tuple(filter(lambda r: current_sel.contains(r), all_regions))

        if len(all_regions) > 0:
            current_sel.clear()
            current_sel.add_all(all_regions)


class KingSelectCsvFieldCommand(sublime_plugin.TextCommand):
    def onDone(self, text):
        index = {to_non_negative_int(text)}
        current_sel = self.view.sel()
        condition_regions = get_current_sel(current_sel, self.view)
        all_regions = []
        for region in condition_regions:
            region = self.view.line(region)
            for line_region in self.view.split_by_newlines(region):
                line = self.view.substr(line_region)
                parser = parse_csv_line(line)
                try:
                    i = 0
                    for item in parser:
                        if i in index:
                            sel_start, sel_end = item[1], item[2]
                            line_start = line_region.begin()
                            all_regions.append(sublime.Region(line_start + sel_start, line_start + sel_end))
                        i += 1
                except StopIteration:
                    pass    # ignore

        current_sel.clear()
        current_sel.add_all(all_regions)

    def run(self, edit):
        self.view.window().show_input_panel('Select i-th column (start from 0): ', '', self.onDone, None, None)        

        # select_type = settings.load_select_type()
        # pattern = get_select_regex(select_type)

        # current_sel = self.view.sel()
        # all_regions = self.view.find_all(pattern)
        # if len(current_sel) > 1 or not current_sel[0].empty():
        #     all_regions = tuple(filter(lambda r: current_sel.contains(r), all_regions))

        # if len(all_regions) > 0:
        #     current_sel.clear()
        #     for region in all_regions:
        #         current_sel.add(region)

class KingManipulateSelectionCommand(sublime_plugin.TextCommand):
    def run(self, edit, manipulation):
        select_type = settings.load_select_type()
        view = self.view
        calculator = Calculator(manipulation)
        current_sel = view.sel()
        all_regions = []

        i = 0
        for sel in current_sel:
            result = calculator.calculate(i=i, x=float(view.substr(sel)))
            if result:
                all_regions.append(sel)
            i += 1

        current_sel.clear()
        current_sel.add_all(all_regions)


class KingWonderfullyManipulateSelectionCommand(sublime_plugin.TextCommand):
    def onDone(self, text):
        settings.set_last_used_selection_predicate(text)
        self.view.run_command('king_manipulate_selection', {'manipulation': text})

    def askFormula(self):
        self.view.window().show_input_panel("Please enter the predicate formula (you may use 'x' and 'i'):",
                                            settings.load_last_used_selection_predicate(),
                                            self.onDone,
                                            None,
                                            None)

    def run(self, edit):
        self.askFormula()


class KingManipulateNumberCommand(sublime_plugin.TextCommand):
    def run(self, edit, manipulation):
        select_type = settings.load_select_type()
        view = self.view
        view.run_command('select_number')
        calculator = Calculator(manipulation)
        current_sel = view.sel()

        i = 0
        if select_type == 'float':
            for sel in current_sel:
                result = calculator.calculate(i=i, x=float(view.substr(sel)))
                if type(result) is 'float' and float.is_integer(result):
                    result = int(result)
                view.replace(edit, sel, str(result))
                i += 1
        elif select_type == 'int':
            for sel in current_sel:
                result = calculator.calculate(i=i, x=int(view.substr(sel)))
                view.replace(edit, sel, str(result))
                i += 1


class KingWonderfulManipulateCommand(sublime_plugin.TextCommand):
    def onDone(self, text):
        settings.set_last_used_formula(text)
        self.view.run_command('king_manipulate_number', {'manipulation': text})

    def askFormula(self):
        self.view.window().show_input_panel("Please enter the batch formula. The variable 'x' will be substituted.",
                                            settings.load_last_used_formula(),
                                            self.onDone,
                                            None,
                                            None)

    def run(self, edit):
        self.askFormula()



