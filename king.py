
import sublime
import sublime_plugin
from ast import NodeTransformer, parse
import os
import sys

BASE_DIR = os.path.dirname(__file__)
sys.path.append(BASE_DIR)
sys.path.extend(map(lambda x: os.path.join(BASE_DIR, x), ['core']))

from core import *


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


class KingInterlacedSelectCommand(sublime_plugin.TextCommand):
    def onDone(self, text):
        count = utils.to_positive_int(text)
        
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



