import numpy as np


class HeatEquationSolver:
    def __init__(self, T=50, n=10, m=25000):
        self.T = T
        self.n = n
        self.m = m
        self.gamma = np.sqrt(2.0)
        self.h = 1.0 / n
        self.tau = T / m
        self.x = np.linspace(0, 1, n + 1)
        self.t = np.linspace(0, T, m + 1)
        self.u = np.zeros((m + 1, n + 1))

        # Функции по умолчанию
        self.u0_func = lambda x: -x ** 2 + 4 * x + 1
        self.left_bc = lambda t: 1.0
        self.right_bc = lambda t: 4.0
        self.source_func = lambda x, t: x * np.cos(t)

    def check_stability_condition(self):
        """Проверяет условие устойчивости явной схемы"""
        stability_condition = self.tau < (self.h ** 2 / (2 * self.gamma ** 2))
        return stability_condition

    def solve(self):
        """Решает уравнение теплопроводности"""
        # Применяем начальное условие
        self.u[0, :] = self.u0_func(self.x)

        # Применяем граничные условия к нулевому слою
        self.u[0, 0] = self.left_bc(0.0)
        self.u[0, -1] = self.right_bc(0.0)

        for k in range(self.m):
            # Граничные условия
            self.u[k + 1, 0] = self.left_bc(self.t[k + 1])
            self.u[k + 1, -1] = self.right_bc(self.t[k + 1])

            # Внутренние узлы
            for i in range(1, self.n):
                diff_term = (self.gamma ** 2) * (self.u[k, i - 1] - 2 * self.u[k, i] + self.u[k, i + 1]) / (self.h ** 2)
                source_term = self.source_func(self.x[i], self.t[k])
                self.u[k + 1, i] = self.u[k, i] + self.tau * (diff_term + source_term)

    def get_layer(self, layer_idx):
        """Возвращает данные для указанного слоя"""
        if layer_idx < 0 or layer_idx >= len(self.u):
            return None, None
        return self.x, self.u[layer_idx, :]

    def create_functions_from_problem_data(self, problem_data):
        """Создает функции условий из данных задачи"""
        try:
            # Создаем безопасное пространство имен для eval
            safe_dict = {
                'x': 0, 't': 0,
                'gamma': self.gamma,
                'cos': np.cos, 'sin': np.sin, 'tan': np.tan,
                'exp': np.exp, 'log': np.log, 'sqrt': np.sqrt,
                'pi': np.pi, 'e': np.e
            }

            # Заменяем математические символы
            def convert_math_symbols(expr):
                expr = expr.replace('²', '**2')
                expr = expr.replace('³', '**3')
                expr = expr.replace('·', '*')
                expr = expr.replace('×', '*')
                expr = expr.replace('÷', '/')
                expr = expr.replace("u''xx", "0")
                expr = expr.replace("u't", "0")
                return expr

            # Начальное условие
            if 'initial_condition' in problem_data:
                init_expr = problem_data['initial_condition'].split('=')[1].strip()
                init_expr = convert_math_symbols(init_expr)
                self.u0_func = lambda x: eval(init_expr, {'builtins': {}}, {**safe_dict, 'x': x})

            # Граничные условия
            if 'left_boundary' in problem_data and 'right_boundary' in problem_data:
                left_expr = problem_data['left_boundary'].split('=')[1].strip()
                right_expr = problem_data['right_boundary'].split('=')[1].strip()
                left_expr = convert_math_symbols(left_expr)
                right_expr = convert_math_symbols(right_expr)

                self.left_bc = lambda t: eval(left_expr, {'builtins': {}}, {**safe_dict, 't': t})
                self.right_bc = lambda t: eval(right_expr, {'builtins': {}}, {**safe_dict, 't': t})

            # Источник
            if 'equation' in problem_data and '+' in problem_data['equation']:
                parts = problem_data['equation'].split('+', 1)
                if len(parts) > 1:
                    source_expr = parts[1].strip()
                    source_expr = convert_math_symbols(source_expr)
                    self.source_func = lambda x, t: eval(source_expr, {'builtins': {}}, {**safe_dict, 'x': x, 't': t})
                else:
                    self.source_func = lambda x, t: 0
            else:
                self.source_func = lambda x, t: 0

            print("Функции успешно созданы из problem.txt")

        except Exception as e:
            print(f"Ошибка создания функций из problem.txt: {e}")