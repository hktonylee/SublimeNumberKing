import sublime, sublime_plugin
from ast import NodeTransformer, Load, Num, Call, Name, Attribute, copy_location, parse, dump


settings = sublime.load_settings("Number King.sublime-settings")


class Calculator(object):
    class CalculatorTransformer(NodeTransformer):
        def visit_Name(self, node):
            if node.id in ("x", "i", "sin", "cos", "tan", "log", "e", "pi"):
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


class KingSelectNumberCommand(sublime_plugin.TextCommand):
    def run(self, edit, select_type='float'):
        if select_type == 'int':
            pattern = '\d+'
        elif select_type == 'float':
            pattern = '\d+(\.\d+)?'
        else:
            raise Exception('Unsupport select number select_type: ' + select_type)

        current_sel = self.view.sel()
        all_regions = []
        for sel in current_sel:
            region = self.view.find(pattern, sel.begin())
            all_regions.append(region)

        current_sel.clear()
        # current_sel.add_all(all_regions)
        for region in all_regions:
            current_sel.add(region)


class KingManipulateNumberCommand(sublime_plugin.TextCommand):
    def run(self, edit, manipulation, select_type='float'):
        view = self.view
        view.run_command('select_number', {'select_type': select_type})
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
        self.setLastUsedFormula(text)
        self.calculator = Calculator(text)
        active_view = self.window.active_view()
        active_view.run_command('select_next_number')
        sels = active_view.sel()
        try:
            edit = active_view.begin_edit()
            i = 0
            for self.position, sel in enumerate(sels):
                result = self.calculator.calculate(int(active_view.substr(sel)), i)
                i += 1
                print("result: " + str(result))
                active_view.replace(edit, sel, str(result))
        finally:
            active_view.end_edit(edit)

    def getLastUsedFormula(self):
        return settings.get("LastUsedFormula") or "x"

    def setLastUsedFormula(self, formula):
        settings.set("LastUsedFormula", formula)

    def askFormula(self):
        self.window.show_input_panel("Please enter the batch formula. The variable 'x' will be substituted.",
                                     self.getLastUsedFormula(),
                                     self.onDone,
                                     None,
                                     None)

    def run(self):
        self.askFormula()



