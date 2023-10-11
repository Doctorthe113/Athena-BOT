from sympy import *
from sympy.plotting import plot_implicit
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
import seaborn as sns

x, y = symbols("x y")

def plot_implicit_better(result_eq, y_result):
    try:
        xmin = solve(result_eq.subs(y, 0), x)[0]
        xmax = solve(result_eq.subs(y, 0), x)[1]
    except: xmin, xmax = 0, 0


    p = plot(y_result[0], (x, xmin, xmax), aspect_ratio = (1, 1), line_color = "cyan", size=(8, 8), adaptive = False, nb_of_points = 10000, show = False)

    for plots in y_result[1:]:
        p.extend(plot(plots, (x, xmin, xmax), aspect_ratio = (1, 1), line_color = "magenta", size=(8, 8), adaptive = False, nb_of_points = 10000, show = False))

    return p
# eq = "2*x + 3*y + 30 = 0"
def symbol_conv(eq):
    equation = eq
    symbol_conv = {"×": "*", 
                    "•": "*", 
                    "√": "sqrt", 
                    "^": "**", 
                    "÷": "/", 
                    "e": "E", #temporarily "removed"
                    "π": "pi", 
                    "sec": "1/cos",
                    "versin": "1 - cos", 
                    "coversin": "1 - sin", 
                    "vercosin": "1 + cos", 
                    "covercosin": "1 + sin",
                    "exsecant": "-1 + sec", 
                    "haversin": "1/2 * 1 - cos",
                    "havercosin": "1/2 * 1 + cos", 
                    "havercoversin": "1/2 * 1 - sin",
                    "havercovercosin": "1/2 * 1 + sin",
                    }
    keys = sorted(symbol_conv.keys(), key = len, reverse = True)
    for k in keys:
        equation = equation.replace(k, symbol_conv[k])

    try:
        transformations = (standard_transformations + (implicit_multiplication_application,))
        parsed = parse_expr(eq.partition("=")[0], transformations=transformations)
        parsed1 = parse_expr(eq.partition("=")[-1], transformations=transformations)
        eq = str(parsed) + "=" + str(parsed1)
    except: pass

    return equation
# will return proccessed equation. `proc_eq`

def eq_calc(proc_eq):
    try: 
        numeric_eq = sympify(str(proc_eq))
        result = (N(numeric_eq, 13))
        int(result)
        # print(result)
        return result
    except: 
        result_eq = sympify(str(proc_eq.translate(str.maketrans({"=": "-"}))))
        x_result = solve(result_eq, x)

        try:
            y_result = solve(result_eq, y)
            # pprint(f"X: {x_result} and Y: {y_result}", use_unicode = True)
            
            try:
                R_side = sympify(str(proc_eq.partition("=")[-1]))
                L_side = sympify(str(proc_eq.partition("=")[0]))

                sns.set_style("whitegrid", 
                            {"grid.color": "0.4", 
                            "grid.linestyle": ":", 
                            "axes.facecolor": "0.1",
                            "xtick.color":"0.4", 
                            "ytick.color":"0.4"})

                p = plot_implicit(Eq(L_side, R_side), 
                                aspect_ratio = (1, 1), 
                                line_color = "tomato", 
                                size=(8, 8), 
                                adaptive = False, 
                                points = 2000, 
                                show = False,
                                x_var=(x, -10, 10), 
                                y_var=(y, -10, 10))
                return x_result, y_result, p
            except:
                return x_result, y_result
        except:
            # pprint(f"X: {x_result}", use_unicode = True)
            return x_result
# will return x_result, y_reult, plot `p` if possible or just x_result, y_reult
# or just x_result

def multiplot(proc_eq):
    equations = proc_eq.split(",")

    sns.set_style("whitegrid", 
                {"grid.color": "0.4", 
                "grid.linestyle": ":", 
                "axes.facecolor": "0.1",
                "xtick.color":"0.4", 
                "ytick.color":"0.4"})

    R_side = simplify(equations[0].partition("=")[-1])
    L_side = simplify(equations[0].partition("=")[0])
    p = plot_implicit(Eq(L_side, R_side), aspect_ratio = (1, 1), line_color = "tomato", show = False, size=(8, 8), adaptive = False, points = 1000)

    try:
        R_side = simplify(equations[1].partition("=")[-1])
        L_side = simplify(equations[1].partition("=")[0])
        p.extend(plot_implicit(Eq(L_side, R_side), aspect_ratio = (1, 1), line_color = "cyan", show = False, size=(8, 8), adaptive = False, points = 1000))
    except:pass

    try:
        R_side = simplify(equations[2].partition("=")[-1])
        L_side = simplify(equations[2].partition("=")[0])
        p.extend(plot_implicit(Eq(L_side, R_side), aspect_ratio = (1, 1), line_color = "springgreen", show = False, size=(8, 8), adaptive = False, points = 1000))
    except:pass

    try:
        R_side = simplify(equations[3].partition("=")[-1])
        L_side = simplify(equations[3].partition("=")[0])
        p.extend(plot_implicit(Eq(L_side, R_side), aspect_ratio = (1, 1), line_color = "orange", show = False, size=(8, 8), adaptive = False, points = 1000))
    except:pass

    try:
        R_side = simplify(equations[4].partition("=")[-1])
        L_side = simplify(equations[4].partition("=")[0])
        p.extend(plot_implicit(Eq(L_side, R_side), aspect_ratio = (1, 1), line_color = "violet", show = False, size=(8, 8), adaptive = False, points = 1000))
    except: pass

    return p
# will return plot(s) `p`