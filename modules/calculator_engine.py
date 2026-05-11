import ast
import math
import operator as op


_ALLOWED_OPS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Mod: op.mod,
    ast.Pow: op.pow,
    ast.UAdd: op.pos,
    ast.USub: op.neg,
}

_ALLOWED_FUNCS = {
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "log": math.log,
    "log10": math.log10,
    "sqrt": math.sqrt,
    "exp": math.exp,
    "abs": abs,
    "round": round,
}

_ALLOWED_CONSTS = {
    "pi": math.pi,
    "e": math.e,
}


def _safe_eval(expression):
    def _eval(node):
        if isinstance(node, ast.Num):
            return node.n
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.Name) and node.id in _ALLOWED_CONSTS:
            return _ALLOWED_CONSTS[node.id]
        if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_OPS:
            return _ALLOWED_OPS[type(node.op)](_eval(node.left), _eval(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_OPS:
            return _ALLOWED_OPS[type(node.op)](_eval(node.operand))
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            func_name = node.func.id
            if func_name not in _ALLOWED_FUNCS:
                raise ValueError("Unsupported function")
            if node.keywords:
                raise ValueError("Keyword arguments not supported")
            args = [_eval(arg) for arg in node.args]
            return _ALLOWED_FUNCS[func_name](*args)
        raise ValueError("Unsupported expression")

    parsed = ast.parse(expression, mode="eval")
    return _eval(parsed.body)


class Calculator:
    def __init__(self):
        self.expression = ""

    def add(self, value):
        self.expression += str(value)

    def operator(self, op_str):
        if not self.expression:
            if op_str == "-":
                self.expression = "-"
            return

        if op_str == "**":
            expression = self.expression.rstrip("+-*/")
            if not expression:
                return
            self.expression = expression + "**"
            return

        if self.expression.endswith("**"):
            self.expression = self.expression[:-2] + op_str
        elif self.expression[-1] in "+-*/":
            self.expression = self.expression[:-1] + op_str
        else:
            self.expression += op_str

    def calculate(self):
        if not self.expression:
            return ""

        expression = self.expression

        while expression and expression[-1] in "+-*/.":
            expression = expression[:-1]

        if not expression:
            return "Error"

        if not expression.endswith("("):
            open_count = expression.count("(") - expression.count(")")
            if open_count > 0:
                expression += ")" * open_count

        try:
            result = _safe_eval(expression)
            if isinstance(result, float) and result.is_integer():
                result = int(result)
            self.expression = str(result)
            return result
        except Exception:
            return "Error"

    def clear(self):
        self.expression = ""
