
import sys
import sublime
import sublime_plugin
from . import utils
from .settings import *
from .calculator import Calculator


def string_to_float(s):
    if s:
        return float(s)
    else:
        return 0.0


def string_to_int(s):
    if s:
        return int(s)
    else:
        return 0


class KingWonderfullyManipulateSelectionCommand(sublime_plugin.TextCommand):
    def on_done(self, text):
        settings.set_last_used_selection_predicate(text)
        self.view.run_command('king_manipulate_number', {'formula': text})

    def ask_formula(self):
        self.view.window().show_input_panel("Please enter the predicate formula (you may use 'x' and 'i'):",
                                            settings.load_last_used_selection_predicate(),
                                            self.on_done,
                                            None,
                                            None)

    def run(self, edit):
        self.ask_formula()


class KingManipulateNumberCommand(sublime_plugin.TextCommand):
    def run(self, edit, formula):
        select_type = settings.load_select_type()
        view = self.view
        view.run_command('select_number')

        try:
            calculator = Calculator(formula)
        except Exception as e:
            sublime.error_message('Error detected in the formula. Please check and correct it.')
            return

        current_sel = view.sel()

        # if select_type == SELECT_TYPE_AUTO:
        #     select_type = utils.infer_select_type()

        if select_type == SELECT_TYPE_AUTO:
            for i, sel in enumerate(current_sel):
                result = calculator.calculate(i=i, x=string_to_float(view.substr(sel)))
                if isinstance(result, float) and float.is_integer(result):
                    result = int(result)
                view.replace(edit, sel, str(result))

        elif select_type == SELECT_TYPE_FLOAT:
            for i, sel in enumerate(current_sel):
                result = calculator.calculate(i=i, x=string_to_float(view.substr(sel)))
                view.replace(edit, sel, str(float(result)))

        elif select_type in (SELECT_TYPE_INT, SELECT_TYPE_INT_NEAREST):
            for i, sel in enumerate(current_sel):
                result = calculator.calculate(i=i, x=string_to_int(view.substr(sel)))
                if select_type == SELECT_TYPE_INT_NEAREST:
                    view.replace(edit, sel, str(int(round(result))))
                else:
                    view.replace(edit, sel, str(int(result)))


class KingWonderfullyManipulateCommand(sublime_plugin.TextCommand):
    def on_done(self, text):
        settings.set_last_used_formula(text)
        self.view.run_command('king_manipulate_number', {'formula': text})

    def askFormula(self):
        self.view.window().show_input_panel("Please enter the batch formula. The variable 'x' will be substituted.",
                                            settings.load_last_used_formula(),
                                            self.on_done,
                                            None,
                                            None)

    def run(self, edit):
        self.askFormula()


