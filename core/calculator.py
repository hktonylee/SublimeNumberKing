
from ast import NodeTransformer, parse


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

