import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import numpy as np

from solver.heat_solver import HeatEquationSolver
from utils.file_io import read_problem_from_file, export_to_file
from utils.convergence_checker import ConvergenceChecker
from .control_panel import ControlPanel
from .plot_area import PlotArea
from .info_panel import InfoPanel


class HeatEquationGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Решение уравнения теплопроводности")
        self.root.geometry("1400x900")
        self.root.configure(bg='#e6f2ff')

        self.solver = None
        self.convergence_checker = ConvergenceChecker(self)
        self.setup_gui()

    def setup_gui(self):
        # Стиль для голубой темы
        style = ttk.Style()
        style.configure('Blue.TFrame', background='#e6f2ff')
        style.configure('Blue.TLabelframe', background='#cce5ff', foreground='#0066cc')
        style.configure('Blue.TLabelframe.Label', background='#cce5ff', foreground='#0066cc')
        style.configure('Blue.TButton', background='#4da6ff', foreground='white')
        style.configure('Title.TLabel', background='#e6f2ff', foreground='#0066cc', font=('Arial', 14, 'bold'))

        # Главный заголовок
        title_label = ttk.Label(self.root, text="ТЕСТОВАЯ ЗАДАЧА", style='Title.TLabel')
        title_label.pack(pady=10)

        # Основной контейнер
        main_container = ttk.Frame(self.root, style='Blue.TFrame')
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Левая панель - управление
        left_panel = ttk.Frame(main_container, style='Blue.TFrame')
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        # Правая панель - графики и информация
        right_panel = ttk.Frame(main_container, style='Blue.TFrame')
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Создаем компоненты
        self.control_panel = ControlPanel(left_panel, self)
        self.info_panel = InfoPanel(right_panel, self)
        self.plot_area = PlotArea(right_panel, self)

    def log_message(self, message):
        """Добавляет сообщение в информационное окно"""
        self.control_panel.info_text.insert(tk.END, message + "\n")
        self.control_panel.info_text.see(tk.END)
        self.root.update()

    def start_calculation(self):
        """Запускает расчет в отдельном потоке"""
        try:
            T = float(self.control_panel.t_var.get())
            n = int(self.control_panel.n_var.get())
            m = int(self.control_panel.m_var.get())
            gamma_squared = float(self.control_panel.gamma_var.get())

            if n <= 0 or m <= 0 or T <= 0 or gamma_squared <= 0:
                messagebox.showerror("Ошибка", "Параметры должны быть положительными числами")
                return

            # Блокируем кнопку расчета
            self.control_panel.calc_button.config(state='disabled', bg='#cccccc')
            self.control_panel.status_var.set("Выполняется расчет")
            self.log_message("=" * 40)
            self.log_message("ЗАПУСК РАСЧЕТА")
            self.log_message("=" * 40)

            self.log_message(f"\nПАРАМЕТРЫ МОДЕЛИ:")
            self.log_message(f"  Коэффициент теплопроводности γ²: {gamma_squared}")
            self.log_message(f"\nПАРАМЕТРЫ РАСЧЕТА:")
            self.log_message(f"  Время T: {T}")
            self.log_message(f"  Узлы по x (n): {n}")
            self.log_message(f"  Слои по t (m): {m}")

            # Запускаем расчет в отдельном потоке
            thread = threading.Thread(target=self.run_calculation, args=(T, n, m, gamma_squared))
            thread.daemon = True
            thread.start()

        except ValueError as e:
            messagebox.showerror("Ошибка", f"Некорректные параметры: {str(e)}")

    def run_calculation(self, T, n, m, gamma_squared):
        """Выполняет расчет в фоновом потоке"""
        try:
            # Создаем решатель с пользовательскими параметрами
            self.solver = HeatEquationSolver(T=T, n=n, m=m)
            # Обновляем коэффициент теплопроводности
            self.solver.gamma = np.sqrt(gamma_squared)

            # Проверка условия устойчивости
            stability_condition = self.solver.check_stability_condition()

            # Показываем результат проверки
            self.plot_area.show_stability_check(stability_condition, self.solver)

            # Читаем данные из файла и создаем функции
            problem_data = read_problem_from_file()
            self.solver.create_functions_from_problem_data(problem_data)

            # Выполняем расчет
            self.solver.solve()

            self.log_message("\nРасчет завершен успешно!")
            self.log_message(f"Всего {m + 1} слоев")
            self.control_panel.status_var.set("Расчет завершен")

        except Exception as e:
            self.log_message(f"Ошибка при расчете: {str(e)}")
            self.control_panel.status_var.set("Ошибка расчета")
        finally:
            # Разблокируем кнопку
            self.root.after(0, lambda: self.control_panel.calc_button.config(state='normal', bg='#4da6ff'))

    def update_problem_info(self):
        """Обновляет информацию о задаче"""
        self.info_panel.update_problem_info()

    def plot_2d(self):
        """Строит 2D график"""
        layers = self.control_panel.parse_layers()
        if layers:
            self.plot_area.plot_2d(self.solver, layers)
            self.log_message(f"Построен двумерный график для слоев: {layers}")

    def plot_3d_points(self):
        """Строит 3D линейный график"""
        layers = self.control_panel.parse_layers()
        if layers:
            self.plot_area.plot_3d_points(self.solver, layers)
            self.log_message(f"Построен трехмерный график для слоев: {layers}")

    def plot_3d_surface(self):
        """Строит 3D поверхность для всех слоев с учетом шага"""
        # Проверяем шаг
        try:
            step_str = self.control_panel.step_var.get().strip()
            step = int(step_str)
            if step <= 0:
                raise ValueError("Шаг должен быть положительным")
        except ValueError:
            messagebox.showerror("Ошибка",
                                 "Введите корректное число для шага\n\n" \
                                 "Шаг должен быть натуральным числом")
            self.control_panel.step_var.set("1")
            return

        # Проверяем наличие расчетов
        if not self.solver:
            messagebox.showerror("Ошибка", "Сначала выполните расчет!")
            return

        # Строим график
        self.plot_area.plot_3d_surface(self.solver, step)
        self.log_message(f"Построена 3D поверхность с шагом {step}")

    def plot_3d_surface_layers(self):
        """Строит 3D поверхность для выбранных слоев"""
        layers = self.control_panel.parse_layers()
        if layers:
            self.plot_area.plot_3d_surface_layers(self.solver, layers)
            self.log_message(f"Построена трехмерная поверхность для слоев: {layers}")

    def export_to_file(self):
        """Экспортирует данные расчета в файл"""
        if not self.solver:
            messagebox.showwarning("Предупреждение", "Сначала выполните расчет")
            return
        step = int(self.control_panel.step_var.get())
        export_to_file(self.solver, step)
        self.log_message(f"Данные экспортированы в файл с шагом {step}")

    def control_calculation(self):
        """Проверка сеточной сходимости с выбором слоев"""
        try:
            if not self.solver:
                messagebox.showwarning("Предупреждение", "Сначала выполните основной расчет!")
                return

            # Создаем диалоговое окно для выбора параметров
            settings_dialog = tk.Toplevel(self.root)
            settings_dialog.title("Настройка проверки сходимости")
            settings_dialog.geometry("570x270")
            settings_dialog.resizable(False, False)
            settings_dialog.transient(self.root)
            settings_dialog.grab_set()

            # Центрируем окно
            settings_dialog.update_idletasks()
            x = (self.root.winfo_screenwidth() - settings_dialog.winfo_width()) // 2
            y = (self.root.winfo_screenheight() - settings_dialog.winfo_height()) // 2
            settings_dialog.geometry(f"+{x}+{y}")

            # Стиль для диалога
            main_frame = ttk.Frame(settings_dialog, style='Blue.TFrame')
            main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

            # Заголовок
            title_label = ttk.Label(main_frame,
                                    text="Настройка проверки сеточной сходимости",
                                    style='Title.TLabel')
            title_label.pack(pady=(0, 15))

            # Поле ввода слоев
            layers_frame = ttk.Frame(main_frame, style='Blue.TFrame')
            layers_frame.pack(fill=tk.X, pady=5)

            ttk.Label(layers_frame, text="Слои для сравнения:", background='#cce5ff').pack(side=tk.LEFT, padx=(0, 5))
            layers_var = tk.StringVar(value="0,125,250,375,500")

            layers_entry = ttk.Entry(layers_frame, textvariable=layers_var, width=25)
            layers_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
            layers_entry.focus()

            # Поле ввода максимального количества итераций
            iterations_frame = ttk.Frame(main_frame, style='Blue.TFrame')
            iterations_frame.pack(fill=tk.X, pady=5)

            ttk.Label(iterations_frame, text="Количество расчетов:", background='#cce5ff').pack(side=tk.LEFT, padx=(0, 5))
            iterations_var = tk.StringVar(value="5")

            iterations_entry = ttk.Entry(iterations_frame, textvariable=iterations_var, width=10)
            iterations_entry.pack(side=tk.LEFT)

            # Подсказки
            hints_frame = ttk.Frame(main_frame, style='Blue.TFrame')
            hints_frame.pack(fill=tk.X, pady=(5, 10))

            hints_text = "• Слои по времени: введите слои базовой сетки для сравнения с результатами на контрольных сетках\n (через запятую, от 1 до 15 слоев)\n" \
                         "• Количество расчетов: для каждого сравнения используется 2 расчета (от 2 до 5 расчетов)"

            hint_label = ttk.Label(hints_frame,
                                   text=hints_text,
                                   background='#cce5ff',
                                   font=('Arial', 8),
                                   foreground='#666666',
                                   justify=tk.LEFT)
            hint_label.pack(anchor=tk.W)

            # Информация о доступных слоях
            max_layer = len(self.solver.t) - 1
            info_label = ttk.Label(main_frame,
                                   text=f"Доступные слои: от 0 до {max_layer}",
                                   background='#cce5ff',
                                   font=('Arial', 9),
                                   foreground='#0066cc')
            info_label.pack(pady=(0, 10))

            def start_check():
                """Запускает проверку сходимости"""
                try:
                    # Парсим параметры
                    layers_str = layers_var.get().strip()
                    iterations_str = iterations_var.get().strip()

                    if not layers_str:
                        messagebox.showerror("Ошибка", "Введите номера слоев")
                        return

                    # Преобразуем строку слоев в список
                    layers_list = [int(l.strip()) for l in layers_str.split(',')]

                    # Проверяем валидность
                    if len(layers_list) > 15:
                        messagebox.showerror("Ошибка", "Можно выбрать не более 15 слоев")
                        return

                    for layer in layers_list:
                        if layer < 0 or layer > max_layer:
                            messagebox.showerror("Ошибка",
                                                 f"Слой {layer} не существует.\nДоступные слои: 0-{max_layer}")
                            return

                    # Преобразуем количество итераций
                    try:
                        max_iterations = int(iterations_str)
                        if max_iterations < 2 or max_iterations > 10:
                            raise ValueError
                    except ValueError:
                        messagebox.showerror("Ошибка", "Количество итераций должно быть от 2 до 10")
                        return

                    # Закрываем диалог
                    settings_dialog.destroy()

                    # Получаем базовые параметры
                    T = float(self.control_panel.t_var.get())
                    base_n = int(self.control_panel.n_var.get())
                    base_m = int(self.control_panel.m_var.get())

                    # Логируем начало проверки
                    self.log_message("=" * 40)
                    self.log_message("ПРОВЕРКА СЕТОЧНОЙ СХОДИМОСТИ")
                    self.log_message("=" * 40)
                    self.log_message(f"Слои для сравнения: {layers_list}")
                    self.log_message(f"Количество расчетов: {max_iterations}")

                    # Запускаем в отдельном потоке
                    thread = threading.Thread(target=self.run_convergence_check,
                                              args=(T, base_n, base_m, layers_list, max_iterations))
                    thread.daemon = True
                    thread.start()

                except ValueError:
                    messagebox.showerror("Ошибка", "Некорректный формат слоев. Используйте: 0,125,250,375,500")
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Ошибка: {str(e)}")

            # Кнопка запуска
            start_button = tk.Button(main_frame,
                                     text="ЗАПУСТИТЬ ПРОВЕРКУ",
                                     command=start_check,
                                     bg='#4da6ff',
                                     fg='white',
                                     font=('Arial', 10, 'bold'),
                                     width=25,
                                     padx=20,
                                     pady=20)
            start_button.pack(pady=8, fill=tk.X, padx=30)

            # Обработка нажатия Enter
            layers_entry.bind('<Return>', lambda e: start_check())
            iterations_entry.bind('<Return>', lambda e: start_check())

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при запуске проверки: {str(e)}")

    def run_convergence_check(self, T, base_n, base_m, layers, max_iterations):
        """Запускает проверку сходимости в фоновом потоке"""
        try:
            # Используем ConvergenceChecker
            results = self.convergence_checker.check_convergence(
                base_n=base_n,
                base_m=base_m,
                T=T,
                layers=layers,
                max_iterations=max_iterations
            )

            if results:
                # Показываем результаты
                self.root.after(0, lambda: self.show_convergence_results(results))

                # Логируем итоги
                final_diff = results[-1]['max_diff']
                iterations_done = len(results)

                self.log_message(f"Выполнено расчетов: {iterations_done}")

            else:
                self.log_message("Ошибка при проверке сходимости")

        except Exception as e:
            self.log_message(f"Ошибка при проверке сходимости: {str(e)}")

    def show_convergence_results(self, results):
        """Показывает результаты проверки сходимости"""
        try:
            self.plot_area.show_convergence_results(results)
        except Exception as e:
            print(f"Ошибка при отображении результатов: {e}")