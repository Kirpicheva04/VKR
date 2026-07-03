import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import tkinter as tk
from tkinter import ttk, messagebox


class PlotArea:
    def __init__(self, parent, main_app):
        self.parent = parent
        self.main_app = main_app
        self.setup_plot_area()

    def setup_plot_area(self):
        # Область для графиков
        plot_frame = ttk.LabelFrame(self.parent, text="ГРАФИКИ РЕШЕНИЯ", style='Blue.TLabelframe')
        plot_frame.pack(fill=tk.BOTH, expand=True)

        # Главный контейнер для графика
        main_plot_container = ttk.Frame(plot_frame, style='Blue.TFrame')
        main_plot_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Контейнер для графика
        graph_container = ttk.Frame(main_plot_container, style='Blue.TFrame')
        graph_container.pack(fill=tk.BOTH, expand=True)

        # Создаем фигуру matplotlib
        self.fig = Figure(figsize=(8, 6), facecolor='white')
        self.canvas = FigureCanvasTkAgg(self.fig, graph_container)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Начальный график с информацией
        self.show_welcome_plot()

    def show_welcome_plot(self):
        """Показывает приветственный график"""
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        ax.set_facecolor('#f0f8ff')

        # Отображаем информацию о программе
        info_text = 'Добро пожаловать!\n\n' \
                    'Для начала работы:\n' \
                    '1. Задайте параметры модели и расчета\n' \
                    '2. Нажмите "Запустить расчет"\n' \
                    '3. Используйте кнопки визуализации\n\n'

        ax.text(0.5, 0.5, info_text, horizontalalignment='center',
                verticalalignment='center', transform=ax.transAxes,
                fontsize=12, color='#0066cc')
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_title('Решение уравнения теплопроводности',
                     color='#0066cc', fontsize=14, pad=20)

        self.canvas.draw()

    def show_stability_check(self, stability_condition, solver):
        """Показывает проверку устойчивости"""
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        ax.set_facecolor('white')

        if stability_condition:
            status_text = "Условие устойчивости ВЫПОЛНЯЕТСЯ\n\n"
            status_color = '#0066cc'
        else:
            status_text = "Условие устойчивости НЕ ВЫПОЛНЯЕТСЯ!\n\n"
            status_color = '#ff6666'

        stability_text = status_text + \
                         f"τ = {solver.tau:.6f}\n" \
                         f"h²/(2*γ²) = {solver.h ** 2 / (2 * solver.gamma ** 2):.6f}\n\n" \
                         "τ < h²/(2*γ²)"

        instructions_text = "Для построения графиков решения\n" \
                            "выберите команду из раздела 'ВИЗУАЛИЗАЦИЯ'"

        if not stability_condition:
            instructions_text += "\n\nРекомендации:\n" \
                                 "• Увеличьте количество слоев (m)\n" \
                                 "• Уменьшите время расчета (T)\n" \
                                 "• Увеличьте количество узлов (n)\n" \
                                 "• Уменьшите коэффициент γ²"

        # Верхняя рамка с информацией об устойчивости
        ax.text(0.5, 0.7, stability_text, horizontalalignment='center',
                verticalalignment='center', transform=ax.transAxes,
                fontsize=12, color=status_color, linespacing=1.5,
                bbox=dict(boxstyle="square,pad=1.5", facecolor='#f0f8ff', edgecolor=status_color))

        # Нижняя рамка с инструкциями
        ax.text(0.5, 0.15, instructions_text, horizontalalignment='center',
                verticalalignment='center', transform=ax.transAxes,
                fontsize=12, color='#0066cc', linespacing=1.5,
                bbox=dict(boxstyle="square,pad=0.5", facecolor='#f0f8ff', edgecolor='#0066cc'))

        ax.set_xticks([])
        ax.set_yticks([])
        ax.axis('off')
        ax.set_title('Проверка устойчивости схемы', color='#0066cc', fontsize=14)

        self.canvas.draw()

    def plot_2d(self, solver, layers):
        if solver is None or not hasattr(solver, 'u') or solver.u is None:
            messagebox.showerror("Ошибка", "Сначала выполните расчет!")
            return

        """Строит 2D график"""
        try:

            self.fig.clear()
            ax = self.fig.add_subplot(111)
            ax.set_facecolor('#f0f8ff')

            colors = ['#0066cc', '#0099ff', '#00ccff', '#66d9ff']

            for idx, layer in enumerate(layers):
                x, u_layer = solver.get_layer(layer)
                if x is not None:
                    color = colors[idx % len(colors)]
                    ax.plot(x, u_layer, 'o-', linewidth=2, markersize=4,
                            color=color, label=f'Слой {layer} (t={solver.t[layer]:.4f})')

            ax.set_xlabel('x', color='#0066cc', fontsize=12)
            ax.set_ylabel('u(x,t)', color='#0066cc', fontsize=12)
            ax.set_title(f'Распределение температуры на отрезке [0,1], слои {layers}',
                         color='#0066cc', fontsize=14)
            ax.grid(True, alpha=0.3, color='#66b3ff')
            ax.legend(facecolor='#f0f8ff', edgecolor='#0066cc')
            ax.tick_params(colors='#0066cc')

            self.canvas.draw()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при построении двумерного графика: {str(e)}")

    def plot_3d_points(self, solver, layers):
        if solver is None or not hasattr(solver, 'u') or solver.u is None:
            messagebox.showerror("Ошибка", "Сначала выполните расчет!")
            return

        """Строит 3D линейный график"""
        try:
            self.fig.clear()
            ax = self.fig.add_subplot(111, projection='3d')

            # Цвета для разных слоев
            colors = ['#0066cc', '#0099ff', '#00ccff', '#66d9ff', '#33adff']

            for idx, layer in enumerate(layers):
                x, u_layer = solver.get_layer(layer)
                if x is not None:
                    color = colors[idx % len(colors)]
                    # Создаем массив времени для текущего слоя
                    t_layer = np.full_like(x, solver.t[layer])
                    # Строим линию для этого слоя
                    ax.plot(x, t_layer, u_layer,
                            color=color,
                            linewidth=2.5,
                            marker='o',
                            markersize=4,
                            label=f'Слой {layer} (t={solver.t[layer]:.4f})')

            # Настройка осей с увеличенным расстоянием
            ax.set_xlabel('x', color='#0066cc', labelpad=15)
            ax.set_ylabel('t', color='#0066cc', labelpad=15)
            ax.set_zlabel('u(x,t)', color='#0066cc', labelpad=15)
            ax.set_title(f'Распределение температуры на отрезке [0,1], слои {layers}', color='#0066cc', pad=20)
            ax.view_init(elev=35, azim=-140)

            # Добавляем легенду с отступом от графика
            legend = ax.legend(facecolor='#f0f8ff',
                               edgecolor='#0066cc',
                               loc='center left',
                               bbox_to_anchor=(-0.80, 0.5),
                               fontsize=10)

            # Настройка цветовой схемы
            ax.xaxis.pane.set_facecolor('#f0f8ff')
            ax.yaxis.pane.set_facecolor('#f0f8ff')
            ax.zaxis.pane.set_facecolor('#f0f8ff')

            # Настройка сетки
            ax.grid(True, alpha=0.3, color='#66b3ff')

            self.canvas.draw()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при построении трехмерного графика: {str(e)}")

    def plot_3d_surface(self, solver, step):
        """Строит 3D поверхность для всех слоев с учетом шага"""
        if solver is None or not hasattr(solver, 'u') or solver.u is None:
            messagebox.showerror("Ошибка", "Сначала выполните расчет!")
            return

        try:
            # Проверяем, что step является целым числом (на всякий случай)
            if not isinstance(step, int):
                step = int(step)

            # Создаем список слоев с заданным шагом
            layers = list(range(0, len(solver.t), step))

            if not layers:
                messagebox.showerror("Ошибка", "Нет слоев для отображения")
                return

            self.fig.clear()
            ax = self.fig.add_subplot(111, projection='3d')

            # Используем только слои с заданным шагом
            X, T = np.meshgrid(solver.x, solver.t[layers])
            U = solver.u[layers, :]

            surf = ax.plot_surface(X, T, U, cmap='Blues', alpha=0.8)

            # Настройка осей
            ax.set_xlabel('x', color='#0066cc', labelpad=15)
            ax.set_ylabel('t', color='#0066cc', labelpad=15)
            ax.set_zlabel('u(x,t)', color='#0066cc', labelpad=15)
            ax.set_title(f'Поверхность u(x, t)', color='#0066cc', pad=20)

            ax.view_init(elev=35, azim=-140)

            # Цветовая шкала
            cbar = self.fig.colorbar(surf, ax=ax, shrink=0.6, aspect=20, pad=0.15)
            cbar.ax.tick_params(colors='#0066cc')
            cbar.set_label('u(x,t)', color='#0066cc')

            # Настройка цветовой схемы
            ax.xaxis.pane.set_facecolor('#f0f8ff')
            ax.yaxis.pane.set_facecolor('#f0f8ff')
            ax.zaxis.pane.set_facecolor('#f0f8ff')

            self.canvas.draw()

        except ValueError as e:
            # Если step некорректен (не int или приводит к ошибке в range)
            messagebox.showerror("Ошибка", f"Некорректный шаг: {str(e)}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при построении 3D поверхности: {str(e)}")

    def plot_3d_surface_layers(self, solver, layers):
        if solver is None or not hasattr(solver, 'u') or solver.u is None:
            messagebox.showerror("Ошибка", "Сначала выполните расчет!")
            return

        """Строит 3D поверхность для выбранных слоев"""
        try:
            layers_sorted = sorted(layers)

            selected_x, selected_t, selected_u = [], [], []
            for layer in layers_sorted:
                x, u_layer = solver.get_layer(layer)
                if x is not None:
                    selected_x.append(x)
                    selected_t.append([solver.t[layer]] * len(x))
                    selected_u.append(u_layer)

            X = np.array(selected_x)
            T = np.array(selected_t)
            U = np.array(selected_u)

            self.fig.clear()
            ax = self.fig.add_subplot(111, projection='3d')

            surf = ax.plot_surface(X, T, U, cmap='Blues', alpha=0.8)

            # Настройка осей с увеличенным расстоянием
            ax.set_xlabel('x', color='#0066cc', labelpad=15)
            ax.set_ylabel('t', color='#0066cc', labelpad=15)
            ax.set_zlabel('u(x,t)', color='#0066cc', labelpad=15)
            ax.set_title(f'Поверхность распределения температуры на отрезке [0, 1] слои {layers}', color='#0066cc',
                         pad=20)
            ax.view_init(elev=35, azim=-140)

            # Цветовая шкала с пояснением и увеличенным расстоянием
            cbar = self.fig.colorbar(surf, ax=ax, shrink=0.6, aspect=20, pad=0.15)
            cbar.set_label('u(x,t)', color='#0066cc')
            cbar.ax.tick_params(colors='#0066cc')

            # Настройка цветовой схемы
            ax.xaxis.pane.set_facecolor('#f0f8ff')
            ax.yaxis.pane.set_facecolor('#f0f8ff')
            ax.zaxis.pane.set_facecolor('#f0f8ff')

            self.canvas.draw()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при построении трехмерной поверхности: {str(e)}")


    def show_convergence_results(self, results):
        """Показывает результаты проверки сходимости"""
        try:
            self.fig.clear()
            ax = self.fig.add_subplot(111)
            ax.set_facecolor('white')

            if len(results) < 2:
                print("DEBUG: Недостаточно результатов для отображения")
                ax.text(0.5, 0.5, "Недостаточно данных для анализа",
                        horizontalalignment='center', verticalalignment='center',
                        transform=ax.transAxes, fontsize=12)
                ax.set_xticks([])
                ax.set_yticks([])
                self.canvas.draw()
                return

            # Строим таблицу с результатами
            table_data = []
            headers = ['№ расчета', 'n', 'm', 'Макс. погрешность', 'Порядок сходимости']

            for i, result in enumerate(results):
                if i == 0:
                    # Для первого расчета (базовой сетки) точность - прочерк
                    accuracy_str = "—"
                else:
                    accuracy_str = f"{result['max_diff']:.16f}"

                if i == 0:
                    convergence_str = "—"
                else:
                    if np.isfinite(result['convergence_rate']) and result['convergence_rate'] > 0:
                        convergence_str = f"{result['convergence_rate']:.16f}"
                    else:
                        convergence_str = "—"

                table_data.append([
                    i + 1,
                    result['n'],
                    result['m'],
                    accuracy_str,
                    convergence_str
                ])

            if len(table_data) > 0:
                # Увеличиваем высоту строк и общую высоту таблицы
                table_height = min(0.1 + len(table_data) * 0.1, 0.7)  # Макс 70% высоты

                # ПОДНИМАЕМ таблицу вверх (уменьшаем второй параметр bbox)
                # bbox = [left, bottom, width, height]
                # bottom = 0.5 - table_height/2 - 0.1 (поднимаем на 0.1)
                table_bottom = max(0.5 - table_height / 2 - 0.05, 0.1)  # Не ниже 0.1

                # УВЕЛИЧИВАЕМ ширину таблицы
                table_width = 0.8  # Было 0.7

                # Центрируем по горизонтали с новой шириной
                table_left = (1 - table_width) / 2

                table = ax.table(cellText=table_data,
                                 colLabels=headers,
                                 cellLoc='center',
                                 loc='center',
                                 bbox=[table_left, table_bottom, table_width, table_height])

                # Увеличиваем масштаб ячеек
                table.scale(1.2, 1.8)  # scale(xscale, yscale)

                table.auto_set_font_size(False)
                table.set_fontsize(11)  # Увеличил шрифт

                # Автоматическая ширина столбцов
                table.auto_set_column_width([0, 1, 2, 3, 4])

                # Подсветка
                for i in range(1, len(table_data)):
                    if results[i].get('accuracy_achieved', False):
                        table[(i, 3)].set_facecolor('#90EE90')
                        table[(i, 4)].set_facecolor('#90EE90')

                # Стилизация заголовков
                for j in range(len(headers)):
                    table[(0, j)].set_facecolor('#e6f2ff')
                    table[(0, j)].set_text_props(weight='bold', color='#0066cc', fontsize=12)

            # Добавляем заголовок с отступом сверху
            ax.set_title('Проверка сеточной сходимости',
                         color='#0066cc', fontsize=16, pad=30)  # Увеличил pad
            ax.axis('off')

            # Добавляем пояснения под таблицей
            explanations = (
                "Пояснения:\n"
                "n - число участков по x\n"
                "m - число участков по t\n"
                "Макс. погрешность - максимальный модуль разности численных решений между базовой и контрольной сетками\n"
                "Порядок сходимости - логарифм отношения погрешностей при двукратном сгущении сетки"
            )

            # Добавляем пояснения внизу с рамкой
            ax.text(0.5, -0.15, explanations,
                    horizontalalignment='center',
                    verticalalignment='top',
                    transform=ax.transAxes,
                    fontsize=9,
                    color='#0066cc',
                    bbox=dict(boxstyle="square,pad=0.5",
                              facecolor='#f0f8ff',
                              edgecolor='#0066cc',
                              alpha=0.8))

            ax.axis('off')

            # Регулируем макет, чтобы освободить место для пояснений
            self.fig.tight_layout(rect=[0, 0.1, 1, 0.95])  # rect=[left, bottom, right, top]

            self.canvas.draw()
            print("DEBUG: Таблица успешно создана")

        except Exception as e:
            print(f"DEBUG: Ошибка при создании таблицы: {e}")
            import traceback
            traceback.print_exc()