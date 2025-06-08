import os
import re
from flask import Flask, render_template, request

# Path absolut ke folder templates dan static
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static')) # <-- Ini sekarang akan menunjuk ke folder 'static' yang benar

# Inisialisasi aplikasi Flask
app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)


def parse_equation(equation, variables, target_var):
    left, right = equation.split('=')
    left = left.strip().replace(' ', '')
    right = right.strip()

    coeffs = {var: 0.0 for var in variables}
    pattern = r'([+-]?[\d\.]*)([a-zA-Z]+)'
    matches = re.findall(pattern, left)

    for coef_str, var in matches:
        if var not in variables:
            raise ValueError(f"Variabel '{var}' tidak dikenali, harus salah satu {variables}")
        if coef_str in ['', '+', '-']:
            coef_str += '1'
        coeffs[var] = float(coef_str)

    if target_var not in coeffs:
        raise ValueError(f"Variabel target '{target_var}' tidak ditemukan di persamaan: {equation}")

    a = coeffs[target_var]
    other_vars = {v: c for v, c in coeffs.items() if v != target_var}
    rhs_terms = [right]
    
    for var, coef in other_vars.items():
        rhs_terms.append(f"{-coef}*{var}")
    
    formula = f"({' + '.join(rhs_terms)}) / {a}"
    return formula


def gauss_seidel(formulas, variables, x0, tol=1e-4, max_iter=1000):
    x_old = x0.copy()
    error_history = {v: [] for v in variables}
    iter_table = []

    # Initial guess
    iter_table.append({
        "iter": 0,
        "values": {v: x_old.get(v, '-') for v in variables},  # Safeguard in case of missing values
        "errors": {v: '-' for v in variables}
    })
    
    for v in variables:
        error_history[v].append(0)

    for i in range(1, max_iter + 1):
        x_new = {}
        current_values = x_old.copy()

        for var in variables:
            context = {**current_values, **x_new}
            x_new[var] = eval(formulas[var], {}, context)
            current_values[var] = x_new[var]
        
        errs = {}
        all_zero_error = True
        
        for v in variables:
            n = x_new[v]
            o = x_old[v]
            err = abs((n - o) / n) * 100 if n != 0 else 0
            errs[v] = err
            error_history[v].append(err)
            if err != 0:
                all_zero_error = False

        iter_table.append({
            "iter": i,
            "values": {v: x_new.get(v, '-') for v in variables},  # Safeguard in case of missing values
            "errors": {v: errs.get(v, '-') for v in variables}
        })

        if all_zero_error or max(errs.values()) < tol * 100:
            break

        x_old = x_new

    return iter_table, x_new, error_history


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Retrieve form data
        n = int(request.form['n'])
        variables = [request.form.get(f'var{i}') for i in range(n)]
        variables = [v.strip() for v in variables if v and v.strip()]  # Filter empty and strip spaces
        equations = [request.form.get(f'eq{i}') for i in range(len(variables))]
        
        # Initial guess
        x0 = {}
        for i, v in enumerate(variables):
            try:
                x0[v] = float(request.form.get(f'x0_{i}'))
            except:
                x0[v] = 0.0
        
        # Tolerance level
        tol = float(request.form.get('tol')) / 100

        # Parsing equations into formulas
        formulas = {}
        for i, var in enumerate(variables):
            formulas[var] = parse_equation(equations[i], variables, var)

        print("DEBUG - variables:", variables, type(variables))

        # Perform Gauss-Seidel
        iter_table, solusi, error_history = gauss_seidel(formulas, variables, x0, tol)

        return render_template('index.html', variables=variables, equations=equations, x0=x0, tol=tol,
                               iter_table=iter_table, solusi=solusi, error_history=error_history, n=len(variables))
    else:
        # Default initialization for GET request
        n = int(request.args.get('n', 3))
        variables = ['x', 'y', 'z'] if n == 3 else [f'x{i+1}' for i in range(n)]
        equations = ['' for _ in range(n)]
        x0 = {v: 0 for v in variables}
        tol = 0.05
        
        return render_template('index.html', variables=variables, equations=equations, x0=x0, tol=tol,
                               iter_table=None, solusi=None, error_history=None, n=n)


if __name__ == '__main__':
    app.run(debug=True)
