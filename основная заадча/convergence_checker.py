import numpy as np
import os
from datetime import datetime


class ConvergenceChecker:
    """Класс для проверки сеточной сходимости"""

    def __init__(self, main_app, solver_class):
        self.main_app = main_app
        self.solver_class = solver_class  # Передаем класс решателя
        self.solver = None

    def check_convergence(self, base_n, base_m, T, L, params, init_params, layers, max_iterations=5):
        results = []
        current_n = base_n
        current_m = base_m
        space_factor = 2
        time_factor = 4

        iteration_details = []
        solvers = []

        self.main_app.log_message("")

        for iteration in range(1, max_iterations + 1):
            self.main_app.log_message(f"Расчет {iteration}: n={current_n}, m={current_m}")

            grid_params = {'n': current_n, 'm': current_m, 'T': T, 'L': L}
            current_solver = self.solver_class(params, init_params, grid_params)
            current_solver.solve(self.main_app.log_message)

            solvers.append(current_solver)

            scaled_layers = []
            for layer in layers:
                t_target = layer * (T / base_m)
                k = int(round(t_target * current_m / T))
                k = min(max(k, 0), current_m)
                scaled_layers.append(k)

            self.main_app.log_message(f"  Слои на текущей сетке: {scaled_layers}")

            max_diff_a = 0.0
            max_diff_b = 0.0
            max_diff_c = 0.0
            convergence_rate_a = 0.0
            convergence_rate_b = 0.0
            convergence_rate_c = 0.0

            layer_comparisons = []
            for i, layer in enumerate(layers):
                fine_layer = scaled_layers[i]
                time_val = current_solver.t[fine_layer]

                node_comparisons = []
                for node_idx in range(len(current_solver.x)):
                    node_comparisons.append({
                        'node_idx': node_idx,
                        'x': current_solver.x[node_idx],
                        'a_fine': current_solver.a[fine_layer, node_idx],
                        'b_fine': current_solver.b[fine_layer, node_idx],
                        'c_fine': current_solver.c[fine_layer, node_idx],
                        'a_coarse': None,
                        'b_coarse': None,
                        'c_coarse': None,
                        'diff_a': None,
                        'diff_b': None,
                        'diff_c': None
                    })

                layer_comparisons.append({
                    'layer_num': layer,
                    'time': time_val,
                    'fine_layer': fine_layer,
                    'coarse_layer': None,
                    'node_comparisons': node_comparisons,
                    'max_diff_a': 0.0,
                    'max_diff_b': 0.0,
                    'max_diff_c': 0.0,
                })

            if iteration > 1 and solvers[iteration - 2] is not None:
                prev_detail = iteration_details[-1]

                for i, layer_comp in enumerate(layer_comparisons):
                    for coarse_node in prev_detail['layer_comparisons'][i]['node_comparisons']:
                        coarse_x = coarse_node['x']
                        coarse_a = coarse_node['a_fine']
                        coarse_b = coarse_node['b_fine']
                        coarse_c = coarse_node['c_fine']

                        fine_idx = None
                        for j, fine_node in enumerate(layer_comp['node_comparisons']):
                            if abs(fine_node['x'] - coarse_x) < 1e-10:
                                fine_idx = j
                                break

                        if fine_idx is not None:
                            diff_a = abs(coarse_a - layer_comp['node_comparisons'][fine_idx]['a_fine'])
                            diff_b = abs(coarse_b - layer_comp['node_comparisons'][fine_idx]['b_fine'])
                            diff_c = abs(coarse_c - layer_comp['node_comparisons'][fine_idx]['c_fine'])

                            if diff_a > layer_comp['max_diff_a']:
                                layer_comp['max_diff_a'] = diff_a
                            if diff_b > layer_comp['max_diff_b']:
                                layer_comp['max_diff_b'] = diff_b
                            if diff_c > layer_comp['max_diff_c']:
                                layer_comp['max_diff_c'] = diff_c

                            if diff_a > max_diff_a:
                                max_diff_a = diff_a
                            if diff_b > max_diff_b:
                                max_diff_b = diff_b
                            if diff_c > max_diff_c:
                                max_diff_c = diff_c

                            layer_comp['node_comparisons'][fine_idx]['a_coarse'] = coarse_a
                            layer_comp['node_comparisons'][fine_idx]['b_coarse'] = coarse_b
                            layer_comp['node_comparisons'][fine_idx]['c_coarse'] = coarse_c
                            layer_comp['node_comparisons'][fine_idx]['diff_a'] = diff_a
                            layer_comp['node_comparisons'][fine_idx]['diff_b'] = diff_b
                            layer_comp['node_comparisons'][fine_idx]['diff_c'] = diff_c

                    self.main_app.log_message(f"    t={layer_comp['time']:.6f}, "
                                              f"погрешность a={layer_comp['max_diff_a']:.6e}, "
                                              f"b={layer_comp['max_diff_b']:.6e}, c={layer_comp['max_diff_c']:.6e}")

            # Сохраняем детали итерации
            iteration_details.append({
                'iteration': iteration,
                'n': current_n,
                'm': current_m,
                'max_diff': max(max_diff_a, max_diff_b, max_diff_c),  # для обратной совместимости
                'max_diff_a': max_diff_a,
                'max_diff_b': max_diff_b,
                'max_diff_c': max_diff_c,
                'layer_comparisons': layer_comparisons,
                'convergence_rate': None,
                'convergence_rate_a': None,
                'convergence_rate_b': None,
                'convergence_rate_c': None,
                'solver': current_solver
            })

            # Вычисляем индивидуальные порядки сходимости
            if iteration > 1:
                prev = iteration_details[-2]
                prev_max_a = prev.get('max_diff_a', 0)
                prev_max_b = prev.get('max_diff_b', 0)
                prev_max_c = prev.get('max_diff_c', 0)

                if prev_max_a > 0 and max_diff_a > 0:
                    convergence_rate_a = np.log2(prev_max_a / max_diff_a)
                    iteration_details[-1]['convergence_rate_a'] = convergence_rate_a
                if prev_max_b > 0 and max_diff_b > 0:
                    convergence_rate_b = np.log2(prev_max_b / max_diff_b)
                    iteration_details[-1]['convergence_rate_b'] = convergence_rate_b
                if prev_max_c > 0 and max_diff_c > 0:
                    convergence_rate_c = np.log2(prev_max_c / max_diff_c)
                    iteration_details[-1]['convergence_rate_c'] = convergence_rate_c

                # Общий порядок (максимальный) для обратной совместимости
                iteration_details[-1]['convergence_rate'] = max(
                    [r for r in [convergence_rate_a, convergence_rate_b, convergence_rate_c] if r is not None],
                    default=None
                )

                self.main_app.log_message(f"  Порядок сходимости: a={convergence_rate_a:.6f}, "
                                          f"b={convergence_rate_b:.6f}, c={convergence_rate_c:.6f}")

            results.append({
                'iteration': iteration,
                'n': current_n,
                'm': current_m,
                'max_diff_a': max_diff_a,
                'max_diff_b': max_diff_b,
                'max_diff_c': max_diff_c,
                'convergence_rate_a': convergence_rate_a if iteration > 1 else None,
                'convergence_rate_b': convergence_rate_b if iteration > 1 else None,
                'convergence_rate_c': convergence_rate_c if iteration > 1 else None,
                'accuracy_achieved': False
            })

            current_n *= space_factor
            current_m *= time_factor

        self.main_app.log_message(f"\nПроверка завершена.")
        self.save_report(results, T, L, params, layers, iteration_details)

        return results, iteration_details

    def save_report(self, results, T, L, params, layers, iteration_details):
        """Сохраняет отчет о проверке сходимости в файл"""
        try:
            os.makedirs("results", exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"results/Значения_решения_сходимость_{timestamp}.txt"

            with open(filename, 'w', encoding='utf-8') as f:
                f.write("ЗНАЧЕНИЯ РЕШЕНИЯ ДЛЯ ПРОВЕРКИ СХОДИМОСТИ\n")
                f.write("=" * 100 + "\n")
                f.write(f"Время создания: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"T = {T}, L = {L}\n")
                f.write(f"Параметры модели: ρ_a={params['pa']}, ρ_b={params['pb']}, ρ_c={params['pc']}, "
                        f"k_a={params['ka']}, k_b={params['kb']}, σ_a={params['ga']}, σ_b={params['gb']}, "
                        f"D_a={params['Da']}, D_b={params['Db']}, D_c={params['Dc']}\n")
                f.write("=" * 100 + "\n\n")

                # Вывод данных для каждой сетки
                for detail in iteration_details:
                    f.write(f"СЕТКА {detail['iteration']} (n={detail['n']}, m={detail['m']})\n")
                    f.write("=" * 80 + "\n")
                    f.write(f"Координаты x: {detail['n'] + 1} точек\n")
                    f.write(f"Временные слои t: {detail['m'] + 1} шагов\n")

                    # ИСПРАВЛЕНО: выводим реальные номера слоев на этой сетке
                    actual_layers = [lc['fine_layer'] for lc in detail['layer_comparisons']]
                    f.write(f"Анализируемые слои: {actual_layers}\n\n")

                    for layer_comp in detail['layer_comparisons']:
                        # ИСПРАВЛЕНО: выводим реальный номер слоя
                        f.write(f"Слой {layer_comp['fine_layer']}: t = {layer_comp['time']:.10f}\n")
                        f.write("-" * 80 + "\n")
                        f.write(f"{'x':<15} {'a(x,t)':<20} {'b(x,t)':<20} {'c(x,t)':<20}\n")
                        f.write("-" * 80 + "\n")

                        for node in layer_comp['node_comparisons']:
                            f.write(f"{node['x']:<15.10f} {node['a_fine']:<20.10f} "
                                    f"{node['b_fine']:<20.10f} {node['c_fine']:<20.10f}\n")
                        f.write("\n")

                    f.write("\n")

                # Таблица сходимости
                f.write("ТАБЛИЦА СХОДИМОСТИ\n")
                f.write("=" * 110 + "\n")
                f.write(f"{'Сетка':<8} {'n':<8} {'m':<8} {'h':<12} {'τ':<12} {'Погрешность':<18} {'Порядок':<15}\n")
                f.write("-" * 110 + "\n")

                max_diffs = []
                for i in range(len(iteration_details) - 1):
                    max_diffs.append(iteration_details[i + 1]['max_diff'])

                for idx, detail in enumerate(iteration_details, 1):
                    h = L / detail['n']
                    tau = T / detail['m']

                    if idx == 1:
                        max_diff_str = "—"
                    elif idx - 2 < len(max_diffs):
                        max_diff_str = f"{max_diffs[idx - 2]:.2e}"
                    else:
                        max_diff_str = "—"

                    if idx == 1:
                        convergence_rate_str = "—"
                    elif detail.get('convergence_rate') is not None:
                        rate = detail['convergence_rate']
                        # Если порядок очень маленький или равен 0, ставим прочерк
                        if rate is not None and abs(rate) < 0.01:
                            convergence_rate_str = "—"
                        else:
                            convergence_rate_str = f"{rate:.3f}"
                    else:
                        convergence_rate_str = "—"

                    f.write(f"{idx:<8} {detail['n']:<8} {detail['m']:<8} {h:<12.2e} {tau:<12.2e} "
                            f"{max_diff_str:<18} {convergence_rate_str:<15}\n")

                    f.write("-" * 110 + "\n\n")

            self.main_app.log_message(f"Отчет сохранен: {filename}")
            return filename

        except Exception as e:
            self.main_app.log_message(f"Ошибка сохранения отчета: {e}")
            return None