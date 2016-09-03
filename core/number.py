
import sublime
import sublime_plugin
from core import utils
from settings import *
from calculator import Calculator


class KingWonderfullyManipulateSelectionCommand(sublime_plugin.TextCommand):
    def on_done(self, text):
        settings.set_last_used_selection_predicate(text)
        self.view.run_command('king_manipulate_selection', {'manipulation': text})

    def ask_formula(self):
        self.view.window().show_input_panel("Please enter the predicate formula (you may use 'x' and 'i'):",
                                            settings.load_last_used_selection_predicate(),
                                            self.on_done,
                                            None,
                                            None)

    def run(self, edit):
        self.ask_formula()


class KingManipulateNumberCommand(sublime_plugin.TextCommand):
    def run(self, edit, manipulation):
        select_type = settings.load_select_type()
        view = self.view
        view.run_command('select_number')
        calculator = Calculator(manipulation)
        current_sel = view.sel()

        i = 0

        if select_type == SELECT_TYPE_AUTO:
            select_type = utils.infer_select_type()

        if select_type == SELECT_TYPE_FLOAT:
            for sel in current_sel:
                result = calculator.calculate(i=i, x=float(view.substr(sel)))
                if type(result) is 'float' and float.is_integer(result):
                    result = int(result)
                view.replace(edit, sel, str(result))
                i += 1

        elif select_type == SELECT_TYPE_INT:
            for sel in current_sel:
                result = calculator.calculate(i=i, x=int(view.substr(sel)))
                view.replace(edit, sel, str(result))
                i += 1


class KingWonderfulManipulateCommand(sublime_plugin.TextCommand):
    def on_done(self, text):
        settings.set_last_used_formula(text)
        self.view.run_command('king_manipulate_number', {'manipulation': text})

    def askFormula(self):
        self.view.window().show_input_panel("Please enter the batch formula. The variable 'x' will be substituted.",
                                            settings.load_last_used_formula(),
                                            self.on_done,
                                            None,
                                            None)

    def run(self, edit):
        self.askFormula()


