import numpy as np
import os
from datetime import datetime
from utils.file_io import read_problem_from_file
from solver.heat_solver import HeatEquationSolver


class ConvergenceChecker:
    def __init__(self, main_app):
        self.current_solver = None
        self.main_app = main_app
        self.solver = None

    def save_report(self, results, T, layers, iteration_details=None):
        """Сохраняет отчет о проверке сходимости в файл"""
        try:
            os.makedirs("results", exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"results/Значения_решения_сходимость_{timestamp}.txt"

            with open(filename, 'w', encoding='utf-8') as f:
                # Заголовок
                f.write("ЗНАЧЕНИЯ РЕШЕНИЯ u(x,t) ДЛЯ ПРОВЕРКИ СХОДИМОСТИ\n")
                f.write("=" * 100 + "\n")
                f.write(f"Время создания: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

                if self.main_app.solver:
                    f.write(f"γ² = {self.main_app.solver.gamma ** 2:.1f}, T = {T:.2f}\n")

                f.write("=" * 100 + "\n\n")

                # Вывод данных для каждой сетки
                if iteration_details:
                    for detail_idx, detail in enumerate(iteration_details, 1):
                        f.write(f"СЕТКА {detail_idx} (n={detail['n']}, m={detail['m']})\n")
                        f.write("=" * 80 + "\n")

                        # Определяем анализируемые слои
                        analyzed_layers = []
                        if detail['layer_comparisons']:
                            for lc in detail['layer_comparisons']:
                                analyzed_layers.append(lc['fine_layer'])

                        f.write(f"Координаты x: {detail['n'] + 1} точек\n")
                        f.write(f"Временные слои t: {detail['m'] + 1} шагов\n")
                        f.write(f"Анализируемые слои: {analyzed_layers}\n\n")

                        # Выводим данные для каждого слоя
                        for layer_comp in detail['layer_comparisons']:
                            f.write(f"Слой {layer_comp['fine_layer']}: t = {layer_comp['time']:.10f}\n")
                            f.write("-" * 60 + "\n")
                            f.write(f"{'x':<20}\t\t{'u(x,t)':<20}\n")
                            f.write("-" * 60 + "\n")

                            # Выводим все точки для этого слоя из node_comparisons
                            for node in layer_comp['node_comparisons']:
                                f.write(f"{node['x']:<20.10f}\t{node['u_fine']:<20.10f}\n")

                            f.write("-" * 60 + "\n")

                        f.write("\n\n")

                # Раздел сравнения сеток (только если есть более одной сетки)
                if iteration_details and len(iteration_details) > 1:
                    f.write("СРАВНЕНИЕ ЗНАЧЕНИЙ МЕЖДУ СЕТКАМИ\n")
                    f.write("=" * 100 + "\n\n")

                    # Сначала найдем все максимальные различия для сводной таблицы
                    max_diffs_between_grids = []

                    for comp_idx in range(len(iteration_details) - 1):
                        coarse_detail = iteration_details[comp_idx]  # Более грубая сетка
                        fine_detail = iteration_details[comp_idx + 1]  # Более точная сетка

                        f.write(f"Сравнение {comp_idx + 1}: Сетка {comp_idx + 1} → Сетка {comp_idx + 2}\n")
                        f.write("-" * 80 + "\n")

                        # Для каждого временного слоя
                        num_layers = min(len(coarse_detail['layer_comparisons']),
                                         len(fine_detail['layer_comparisons']))

                        max_diff_for_comparison = 0.0  # Максимальная разность для этого сравнения сеток

                        for i in range(num_layers):
                            coarse_comp = coarse_detail['layer_comparisons'][i]
                            fine_comp = fine_detail['layer_comparisons'][i]

                            # Находим общие точки (ВСЕ узлы из грубой сетки)
                            common_points = []

                            # Берем ВСЕ узлы из грубой сетки
                            for coarse_node in coarse_comp['node_comparisons']:
                                coarse_x = coarse_node['x']
                                coarse_u = coarse_node['u_fine']

                                # Находим ближайшую точку в точной сетке
                                fine_u = None
                                # Поскольку сетка измельчается в 2 раза, точки из грубой сетки
                                # должны быть точно в точной сетке (с двойным разрешением)
                                for fine_node in fine_comp['node_comparisons']:
                                    if abs(fine_node['x'] - coarse_x) < 1e-10:  # Точное совпадение
                                        fine_u = fine_node['u_fine']
                                        break

                                if fine_u is not None:
                                    diff = abs(fine_u - coarse_u)
                                    common_points.append({
                                        'x': coarse_x,
                                        'u_coarse': coarse_u,
                                        'u_fine': fine_u,
                                        'diff': diff
                                    })

                                    if diff > max_diff_for_comparison:
                                        max_diff_for_comparison = diff

                            # Для вывода ограничиваем количество точек, если их слишком много
                            max_points_to_show = 30
                            points_to_show = common_points
                            if len(common_points) > max_points_to_show:
                                # Выбираем равномерно распределенные точки
                                step = len(common_points) // max_points_to_show
                                points_to_show = common_points[::step]

                                # Всегда добавляем граничные точки
                                if len(common_points) > 0:
                                    # Добавляем первую точку
                                    if points_to_show[0]['x'] != common_points[0]['x']:
                                        points_to_show.insert(0, common_points[0])
                                    # Добавляем последнюю точку
                                    if points_to_show[-1]['x'] != common_points[-1]['x']:
                                        points_to_show.append(common_points[-1])

                            f.write(f"Время: {coarse_comp['time']:.8f} (слой {coarse_comp['fine_layer']}) → "
                                    f"{fine_comp['time']:.8f} (слой {fine_comp['fine_layer']})\n")
                            f.write("{:<12}\t\t{:<20}\t{:<20}\t\t{:<20}\n".format(
                                "x", "u_базовой", "u_контрольной", "погрешность"))
                            f.write("-" * 80 + "\n")

                            # Находим максимальную разность для этого слоя
                            layer_max_diff = 0.0
                            for point in common_points:
                                if point['diff'] > layer_max_diff:
                                    layer_max_diff = point['diff']

                            # Выводим сравнения
                            for point in points_to_show:
                                f.write("{:<12.10f}\t\t{:<20.10f}\t{:<20.10f}\t\t{:<20.10f}\n".format(
                                    point['x'],
                                    point['u_coarse'],  # Значение из грубой сетки
                                    point['u_fine'],  # Значение из точной сетки
                                    point['diff']
                                ))

                            f.write(f"Максимальная погрешность: {layer_max_diff:.6e}\n\n")

                        # Сохраняем максимальную разность для этого сравнения сеток
                        max_diffs_between_grids.append(max_diff_for_comparison)
                        f.write(
                            f"Максимальная погрешность из сравнения сеток {comp_idx + 1}→{comp_idx + 2}: {max_diff_for_comparison:.6e}\n\n")

                # Сводная таблица сходимости - ВАЖНО: этот блок должен быть здесь!
                if iteration_details:
                    f.write("ТАБЛИЦА СХОДИМОСТИ\n")
                    f.write("=" * 110 + "\n")
                    f.write("{:<8} {:<8} {:<8} {:<12} {:<12} {:<18} {:<15}\n".format(
                        "Сетка", "n", "m", "h", "τ", "Погрешность", "Порядок"))
                    f.write("-" * 110 + "\n")

                    # Вычисляем максимальные различия между последовательными сетками
                    max_diffs_between_grids = []
                    for comp_idx in range(len(iteration_details) - 1):
                        coarse_detail = iteration_details[comp_idx]
                        fine_detail = iteration_details[comp_idx + 1]

                        max_diff_for_comparison = 0.0
                        num_layers = min(len(coarse_detail['layer_comparisons']),
                                         len(fine_detail['layer_comparisons']))

                        for i in range(num_layers):
                            coarse_comp = coarse_detail['layer_comparisons'][i]
                            fine_comp = fine_detail['layer_comparisons'][i]

                            # Сравниваем ВСЕ точки из грубой сетки
                            for coarse_node in coarse_comp['node_comparisons']:
                                coarse_x = coarse_node['x']
                                coarse_u = coarse_node['u_fine']

                                # Находим соответствующую точку в точной сетке
                                fine_u = None
                                for fine_node in fine_comp['node_comparisons']:
                                    if abs(fine_node['x'] - coarse_x) < 1e-10:
                                        fine_u = fine_node['u_fine']
                                        break

                                if fine_u is not None:
                                    diff = abs(fine_u - coarse_u)
                                    if diff > max_diff_for_comparison:
                                        max_diff_for_comparison = diff

                        max_diffs_between_grids.append(max_diff_for_comparison)

                    for idx, detail in enumerate(iteration_details, 1):
                        h = 1.0 / detail['n']
                        tau = T / detail['m']

                        # Максимальная погрешность
                        if idx == 1:
                            max_diff_str = "—"
                        elif idx - 2 < len(max_diffs_between_grids):
                            max_diff_str = f"{max_diffs_between_grids[idx - 2]:.2e}"
                        else:
                            max_diff_str = "—"

                        # Порядок сходимости
                        if idx == 1:
                            convergence_rate_str = "—"
                        elif 'convergence_rate' in detail and detail['convergence_rate'] is not None:
                            convergence_rate_str = f"{detail['convergence_rate']:.3f}"
                        else:
                            convergence_rate_str = "—"

                        f.write("{:<8} {:<8} {:<8} {:<12.2e} {:<12.2e} {:<18} {:<15}\n".format(
                            idx,
                            detail['n'],
                            detail['m'],
                            h,
                            tau,
                            max_diff_str,
                            convergence_rate_str
                        ))

                    f.write("-" * 110 + "\n\n")

            self.main_app.log_message(f"Отчет сохранен: {filename}")
            return filename

        except Exception as e:
            self.main_app.log_message(f"Ошибка сохранения отчета: {e}")
            import traceback
            self.main_app.log_message(traceback.format_exc())
            return None

    def check_convergence(self, base_n, base_m, T, layers, max_iterations=5):
        """
        Проверка сеточной сходимости с последовательным измельчением сетки.
        """
        results = []
        problem_data = read_problem_from_file()
        current_n = base_n
        current_m = base_m
        space_factor = 2  # по x
        time_factor = 4  # по t

        # Для сбора подробных данных
        iteration_details = []

        # Список решателей для каждой итерации
        solvers = []

        self.main_app.log_message("")

        # Основной цикл по итерациям
        for iteration in range(1, max_iterations + 1):
            self.main_app.log_message(f"Расчет {iteration}: n={current_n}, m={current_m}")

            # Создаем новый решатель
            current_solver = HeatEquationSolver(T=T, n=current_n, m=current_m)

            if self.main_app.solver:
                current_solver.gamma = self.main_app.solver.gamma

            current_solver.create_functions_from_problem_data(problem_data)
            current_solver.solve()

            # Сохраняем решатель
            solvers.append(current_solver)

            # Преобразуем номера слоев для текущей сетки
            scaled_layers = []
            for layer in layers:
                t_target = layer * (T / base_m)
                k = int(round(t_target * current_m / T))
                k = min(max(k, 0), current_m)
                scaled_layers.append(k)

            self.main_app.log_message(f"  Слои на текущей сетке: {scaled_layers}")

            max_diff = 0.0
            convergence_rate = 0.0

            # Для сбора деталей сравнения
            layer_comparisons = []

            # Собираем данные для текущей итерации
            for i, layer in enumerate(layers):
                fine_layer = scaled_layers[i]
                time_val = current_solver.t[fine_layer]

                # Собираем данные по узлам для этого слоя
                node_comparisons = []

                # Выводим все точки для каждой сетки
                for node_idx in range(len(current_solver.x)):
                    node_comparisons.append({
                        'node_idx': node_idx,
                        'x': current_solver.x[node_idx],
                        'u_fine': current_solver.u[fine_layer, node_idx],
                        'u_coarse': None,  # Заполнится при сравнении сеток
                        'diff': None
                    })

                layer_comparisons.append({
                    'layer_num': layer,
                    'time': time_val,
                    'fine_layer': fine_layer,
                    'coarse_layer': None,
                    'node_comparisons': node_comparisons,
                    'max_diff_value': 0.0,
                })

            # Если это не первая, сравниваем с предыдущей сеткой
            if iteration > 1 and solvers[iteration - 2] is not None:
                prev_solver = solvers[iteration - 2]
                prev_detail = iteration_details[-1]

                for i, layer_comp in enumerate(layer_comparisons):
                    fine_layer = layer_comp['fine_layer']
                    coarse_layer = prev_detail['layer_comparisons'][i]['fine_layer']

                    layer_max_diff = 0.0

                    # Сравниваем значения в точках предыдущей (более грубой) сетки
                    for coarse_node in prev_detail['layer_comparisons'][i]['node_comparisons']:
                        coarse_x = coarse_node['x']
                        coarse_u = coarse_node['u_fine']

                        # Находим ближайшую точку в текущей (более точной) сетке
                        fine_u = None
                        fine_idx = None
                        for j, fine_node in enumerate(layer_comp['node_comparisons']):
                            if abs(fine_node['x'] - coarse_x) < 1e-10:  # Точное совпадение
                                fine_u = fine_node['u_fine']
                                fine_idx = j
                                break

                        if fine_u is not None:
                            diff = abs(fine_u - coarse_u)
                            if diff > layer_max_diff:
                                layer_max_diff = diff

                            # Сохраняем данные для вывода
                            layer_comp['node_comparisons'][fine_idx]['u_coarse'] = coarse_u
                            layer_comp['node_comparisons'][fine_idx]['diff'] = diff

                    layer_comp['max_diff_value'] = layer_max_diff

                    if layer_max_diff > max_diff:
                        max_diff = layer_max_diff

                    self.main_app.log_message(f"    t={layer_comp['time']:.6f}, погрешность={layer_max_diff:.6f}")

            # Сохраняем детали итерации
            iteration_details.append({
                'iteration': iteration,
                'n': current_n,
                'm': current_m,
                'max_diff': max_diff,
                'layer_comparisons': layer_comparisons,
                'convergence_rate': convergence_rate if iteration > 1 else None,
                'solver': current_solver
            })

            # Оцениваем порядок сходимости
            if iteration > 1:
                prev_max_diff = iteration_details[-2]['max_diff']
                if prev_max_diff > 0 and max_diff > 0:
                    ratio = prev_max_diff / max_diff
                    convergence_rate = np.log2(ratio)
                    iteration_details[-1]['convergence_rate'] = convergence_rate
                    self.main_app.log_message(f"  Порядок сходимости: {convergence_rate:.6f}")

            # Сохраняем результат итерации
            results.append({
                'iteration': iteration,
                'n': current_n,
                'm': current_m,
                'max_diff': max_diff,
                'convergence_rate': convergence_rate if iteration > 1 else None,
                'accuracy_achieved': False  # Убрана проверка точности
            })

            # Увеличиваем сетку для следующей итерации
            current_n *= space_factor
            current_m *= time_factor

        # Итоговый вывод
        self.main_app.log_message(f"\nПроверка завершена.")

        # Сохраняем отчет
        self.save_report(results, T, layers, iteration_details)

        # Очищаем решатели
        for solver in solvers:
            del solver

        import gc
        gc.collect()

        # Возвращаем упрощенные результаты
        simplified_results = []
        for r in results:
            simplified_results.append({
                'n': r['n'],
                'm': r['m'],
                'max_diff': r['max_diff'],
                'convergence_rate': r['convergence_rate'] if r['convergence_rate'] is not None else 0,
                'accuracy_achieved': r['accuracy_achieved']
            })

        return simplified_results