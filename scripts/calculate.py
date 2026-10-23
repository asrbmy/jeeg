# keywords: calculate, calc, math, maths, compute, solve, evaluate, plus, minus, times, divided, multiply, percent, squared, sum
# desc: Calculate anything (calculate 15% of 200, 12 * (3+4), sqrt 144)
# category: utility
# usage: calculate <expression>
# rawargs: yes
# priority: 1
import ast, math, operator, re
from _lib import args_text, fail
src = args_text()
if not src:
    fail("Usage: calculate <expression>   e.g. calculate 15% of 200")
if len(src) > 200:
    fail("Expression too long.")
s = src.lower().replace(",", "").strip()
s = re.sub(r"^(?:what\s+is|what's|whats|calculate|calc|compute|solve|evaluate)\s+", "", s).rstrip("?=. ")
s = re.sub(r"(\d+(?:\.\d+)?)\s*(?:%|percent)\s*of\s*(\d+(?:\.\d+)?)", r"(\1/100*\2)", s)
s = re.sub(r"(\d+(?:\.\d+)?)\s*percent\b", r"(\1/100)", s)
for pat, rep in ((r"square root of\s*(\d+(?:\.\d+)?)", r"sqrt(\1)"), (r"\bsqrt\s+(\d+(?:\.\d+)?)", r"sqrt(\1)"),
                 (r"multiplied by", "*"), (r"divided by", "/"), (r"to the power of|raised to", "**"),
                 (r"\bsquared\b", "**2"), (r"\bcubed\b", "**3"), (r"\bplus\b", "+"), (r"\bminus\b", "-"),
                 (r"\btimes\b", "*"), (r"\bover\b", "/"), (r"\bmod\b", "%"), (r"(?<=\d)\s*[x×]\s*(?=[\d(])", "*"),
                 (r"÷", "/"), (r"×", "*"), (r"\^", "**")):
    s = re.sub(pat, rep, s)
OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv,
       ast.FloorDiv: operator.floordiv, ast.Mod: operator.mod, ast.Pow: operator.pow}
FUNCS = {"sqrt": math.sqrt, "sin": math.sin, "cos": math.cos, "tan": math.tan, "log": math.log10, "ln": math.log,
         "abs": abs, "round": round, "floor": math.floor, "ceil": math.ceil, "factorial": math.factorial}
CONST = {"pi": math.pi, "e": math.e}
def ev(n):
    if isinstance(n, ast.Expression): return ev(n.body)
    if isinstance(n, ast.Constant) and type(n.value) in (int, float): return n.value
    if isinstance(n, ast.Name) and n.id in CONST: return CONST[n.id]
    if isinstance(n, ast.UnaryOp) and isinstance(n.op, (ast.USub, ast.UAdd)):
        v = ev(n.operand); return -v if isinstance(n.op, ast.USub) else v
    if isinstance(n, ast.BinOp) and type(n.op) in OPS:
        a, b = ev(n.left), ev(n.right)
        if isinstance(n.op, ast.Pow) and (abs(b) > 1000 or (abs(a) > 1e6 and abs(b) > 10)):
            raise ValueError("exponent too large")
        return OPS[type(n.op)](a, b)
    if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in FUNCS and not n.keywords:
        args = [ev(a) for a in n.args]
        if n.func.id == "factorial" and not (len(args) == 1 and float(args[0]).is_integer() and 0 <= args[0] <= 500):
            raise ValueError("factorial needs a whole number from 0 to 500")
        return FUNCS[n.func.id](*([int(args[0])] if n.func.id == "factorial" else args))
    raise ValueError("unsupported")
try:
    v = ev(ast.parse(s, mode="eval"))
except ZeroDivisionError:
    fail("Cannot divide by zero.")
except (ValueError, SyntaxError, TypeError, OverflowError, RecursionError, MemoryError):
    fail("I could not understand that calculation.")
if isinstance(v, float):
    v = int(v) if v.is_integer() and abs(v) < 1e15 else float(format(v, ".10g"))
shown = re.sub(r"^(?:what\s+is|what's|whats|calculate|calc|compute|solve|evaluate)\s+", "", src.strip(), flags=re.I).rstrip("?=. ")
print(f"{shown} = {v:,}" if isinstance(v, int) else f"{shown} = {v}")
