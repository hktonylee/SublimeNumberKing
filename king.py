import sublime, sublime_plugin
from ast import NodeTransformer, Load, Num, Call, Name, Attribute, copy_location, parse, dump
import os


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

settings = Settings()

class Calculator(object):
    class CalculatorTransformer(NodeTransformer):
        def visit_Name(self, node):
            if node.id in ('ceil', 'copysign', 'fabs', 'factorial', 'floor', 'fmod', 'frexp', 'fsum', 'isfinite', 'isinf', 'isnan', 'ldexp', 'modf', 'trunc', 'exp', 'expm1', 'log', 'log1p', 'log2', 'log10', 'pow', 'pow', 'sqrt', 'acos', 'asin', 'atan', 'atan2', 'cos', 'hypot', 'sin', 'tan', 'degrees', 'radians', 'acosh', 'asinh', 'atanh', 'cosh', 'sinh', 'tanh', 'erf', 'erfc', 'gamma', 'lgamma', 'pi', 'e', ):
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
        for key, value in kwargs.iteritems():
            self.ns[key] = value
        return eval(self.code, self.ns)


class KingNeedHelpCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        path = os.path.join(sublime.packages_path(), 'Number King', 'README.md')
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
        for region in all_regions:
            current_sel.add(region)


class KingInterlacedSelectCommand(sublime_plugin.WindowCommand):
    def onDone(self, text):
        try:
            count = int(text)
        except ValueError:
            sublime.error_message('Interlaced count must be integer.')
        # TODO: 

    def askInterlacedCount(self):
        self.window.show_input_panel('Please the interlaced count',
                                     1,
                                     self.onDone,
                                     None,
                                     None)

    def run(self):
        self.askInterlacedCount()


class KingSelectAllNumbersCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        select_type = settings.load_select_type()
        pattern = get_select_regex(select_type)

        current_sel = self.view.sel()
        all_regions = self.view.find_all(pattern)
        all_regions = list(filter(lambda r: current_sel.contains(r), all_regions))

        current_sel.clear()
        for region in all_regions:
            current_sel.add(region)


class KingManipulateNumberCommand(sublime_plugin.TextCommand):
    def run(self, edit, manipulation):
        select_type = settings.load_select_type()
        view = self.view
        view.run_command('select_number')
        calculator = Calculator(manipulation)
        current_sel = view.sel()

        if select_type == 'int':
            transformer = int
        elif select_type == 'float':
            transformer = float

        i = 0
        for sel in current_sel:
            result = calculator.calculate(i=i, x=transformer(view.substr(sel)))
            view.replace(edit, sel, str(result))
            i += 1


class KingWonderfulManipulateCommand(sublime_plugin.WindowCommand):
    def onDone(self, text):
        settings.set_last_used_formula(text)
        self.calculator = Calculator(text)
        active_view = self.window.active_view()
        active_view.run_command('select_next_number')
        sels = active_view.sel()
        try:
            edit = active_view.begin_edit()
            i = 0
            for self.position, sel in enumerate(sels):
                result = self.calculator.calculate(i=i, x=int(active_view.substr(sel)))
                i += 1
                active_view.replace(edit, sel, str(result))
        finally:
            active_view.end_edit(edit)

    def askFormula(self):
        self.window.show_input_panel("Please enter the batch formula. The variable 'x' will be substituted.",
                                     settings.load_last_used_formula(),
                                     self.onDone,
                                     None,
                                     None)

    def run(self):
        self.askFormula()



