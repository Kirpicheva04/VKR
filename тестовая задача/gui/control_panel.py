import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox


class ControlPanel:
    def __init__(self, parent, main_app):
        self.parent = parent
        self.main_app = main_app
        self.setup_control_panel()

    def setup_control_panel(self):
        # Параметры МОДЕЛИ
        model_frame = ttk.LabelFrame(self.parent, text="ПАРАМЕТРЫ МОДЕЛИ", style='Blue.TLabelframe')
        model_frame.pack(fill=tk.X, pady=(0, 10))

        # Коэффициент теплопроводности
        ttk.Label(model_frame, text="Коэффициент теплопроводности (γ²):", background='#cce5ff').grid(row=0, column=0,
                                                                                                     sticky=tk.W,
                                                                                                     padx=5, pady=2)
        self.gamma_var = tk.StringVar(value="2.0")
        ttk.Entry(model_frame, textvariable=self.gamma_var, width=15).grid(row=0, column=1, padx=(0, 10), pady=2)

        # Параметры РАСЧЕТА (T, n, m)
        params_frame = ttk.LabelFrame(self.parent, text="ПАРАМЕТРЫ РАСЧЕТА", style='Blue.TLabelframe')
        params_frame.pack(fill=tk.X, pady=(0, 10))

        # Время T
        ttk.Label(params_frame, text="Конечное время (T):", background='#cce5ff').grid(row=0, column=0, sticky=tk.W,
                                                                                       padx=5, pady=2)
        self.t_var = tk.StringVar(value="50")
        ttk.Entry(params_frame, textvariable=self.t_var, width=15).grid(row=0, column=1, padx=(0, 10), pady=2)

        # Узлы по x (n)
        ttk.Label(params_frame, text="Число участков по x (n):", background='#cce5ff').grid(row=1, column=0,
                                                                                            sticky=tk.W, padx=5, pady=2)
        self.n_var = tk.StringVar(value="10")
        ttk.Entry(params_frame, textvariable=self.n_var, width=15).grid(row=1, column=1, padx=(0, 10), pady=2)

        # Слои по t (m)
        ttk.Label(params_frame, text="Число участков по t (m):", background='#cce5ff').grid(row=2, column=0,
                                                                                            sticky=tk.W, padx=5, pady=2)
        self.m_var = tk.StringVar(value="25000")
        ttk.Entry(params_frame, textvariable=self.m_var, width=15).grid(row=2, column=1, padx=(0, 10), pady=2)



        params_frame.columnconfigure(0, weight=1)
        params_frame.columnconfigure(1, weight=1)

        # Фрейм для кнопок расчета
        buttons_frame = ttk.Frame(params_frame, style='Blue.TFrame')
        buttons_frame.grid(row=3, column=0, columnspan=2, pady=10, sticky=tk.EW)

        # Кнопка запуска расчета
        self.calc_button = tk.Button(buttons_frame, text="ЗАПУСТИТЬ РАСЧЕТ",
                                     command=self.main_app.start_calculation,
                                     bg='#4da6ff', fg='white', font=('Arial', 10, 'bold'),
                                     relief=tk.RAISED, bd=3, width=19)
        self.calc_button.pack(side=tk.LEFT, padx=(0, 5), expand=True, fill=tk.X)

        # Кнопка проверки сходимости
        self.control_button = tk.Button(buttons_frame, text="ПРОВЕРКА СХОДИМОСТИ",
                                        command=self.main_app.control_calculation,
                                        bg='#66b3ff', fg='white', font=('Arial', 10, 'bold'),
                                        relief=tk.RAISED, bd=3, width=20)
        self.control_button.pack(side=tk.RIGHT, padx=(5, 0), expand=True, fill=tk.X)

        # ВИЗУАЛИЗАЦИЯ
        viz_frame = ttk.LabelFrame(self.parent, text="ВИЗУАЛИЗАЦИЯ", style='Blue.TLabelframe')
        viz_frame.pack(fill=tk.X, pady=(0, 10))

        # БЛОК 1: Выбор слоев
        layer_select_frame = ttk.Frame(viz_frame, style='Blue.TFrame')
        layer_select_frame.pack(fill=tk.X, padx=5, pady=5)

        # Надпись и поле ввода в одной строке
        layer_input_frame = ttk.Frame(layer_select_frame, style='Blue.TFrame')
        layer_input_frame.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(layer_input_frame, text="Выбрать слои:", background='#cce5ff').pack(side=tk.LEFT, padx=(0, 5))
        self.layers_var = tk.StringVar(value="0,1")
        ttk.Entry(layer_input_frame, textvariable=self.layers_var, width=15).pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Кнопки визуализации слоев
        layer_buttons_frame = ttk.Frame(layer_select_frame, style='Blue.TFrame')
        layer_buttons_frame.pack(fill=tk.X)

        # Контейнер для центрирования кнопок
        center_frame = ttk.Frame(layer_buttons_frame, style='Blue.TFrame')
        center_frame.pack(expand=True)

        tk.Button(center_frame, text="2D слои", command=self.main_app.plot_2d,
                  bg='#66b3ff', fg='white', width=12).pack(side=tk.LEFT, padx=2, pady=2)
        tk.Button(center_frame, text="3D слои", command=self.main_app.plot_3d_points,
                  bg='#66b3ff', fg='white', width=12).pack(side=tk.LEFT, padx=2, pady=2)
        tk.Button(center_frame, text="Поверхность", command=self.main_app.plot_3d_surface_layers,
                  bg='#66b3ff', fg='white', width=12).pack(side=tk.LEFT, padx=2, pady=2)

        # БЛОК 2: Шаг просмотра
        step_frame = ttk.Frame(viz_frame, style='Blue.TFrame')
        step_frame.pack(fill=tk.X, padx=5, pady=5)

        # Верхняя строка: надпись, поле ввода и кнопка
        step_row_frame = ttk.Frame(step_frame, style='Blue.TFrame')
        step_row_frame.pack(fill=tk.X, pady=(0, 5))

        tk.Button(step_row_frame, text="Все слои", command=self.main_app.plot_3d_surface,
                  bg='#66b3ff', fg='white', width=12).pack(side=tk.LEFT, padx=(15, 20))
        ttk.Label(step_row_frame, text="Выбрать шаг просмотра:", background='#cce5ff').pack(side=tk.LEFT, padx=(0, 5))
        self.step_var = tk.StringVar(value="1")
        ttk.Entry(step_row_frame, textvariable=self.step_var, width=8).pack(side=tk.LEFT)

        # Инструкция внизу отдельной строкой
        instruction_label = ttk.Label(step_frame,
                                      text="Шаг 1: каждый слой, Шаг 2: слои 0,2,4... , Шаг 3: слои 0,3,6...",
                                      background='#cce5ff',
                                      font=('Arial', 8),
                                      foreground='#666666')
        instruction_label.pack(anchor=tk.W)

        # Кнопка вывода данных в файл
        export_button = tk.Button(step_frame, text="ВЫВОД ДАННЫХ В ФАЙЛ",
                                  command=self.main_app.export_to_file,
                                  bg='#66b3ff', fg='white',
                                  font=('Arial', 9, 'bold'),
                                  relief=tk.RAISED, bd=2)
        export_button.pack(fill=tk.X, pady=(5, 0))

        # Информация о расчете
        info_frame = ttk.LabelFrame(self.parent, text="ИСТОРИЯ РАСЧЕТОВ", style='Blue.TLabelframe')
        info_frame.pack(fill=tk.BOTH, expand=True)

        self.info_text = scrolledtext.ScrolledText(info_frame, height=12, width=40,
                                                   bg='#f0f8ff', fg='#0066cc')
        self.info_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Статус бар
        self.status_var = tk.StringVar(value="Готов к работе")
        status_label = tk.Label(self.parent, textvariable=self.status_var,
                                bg='#cce5ff', fg='#0066cc', relief=tk.SUNKEN,
                                font=('Arial', 9))
        status_label.pack(fill=tk.X, pady=(10, 0))

    def parse_layers(self):
        """Парсит строку с номерами слоев"""
        try:
            layers_str = self.layers_var.get()
            layers = [int(l.strip()) for l in layers_str.split(',')]

            # Проверка на неболее чем 15 указанных слоёв:
            if len(layers) > 15:
                messagebox.showerror("Ошибка", "Можно выбрать не более 15 слоев")
                return None
            # Конец добавления

            if self.main_app.solver:
                max_layer = len(self.main_app.solver.t) - 1
                for layer in layers:
                    if layer < 0 or layer > max_layer:
                        messagebox.showerror("Ошибка",
                                             f"Слой {layer} не существует.\n"
                                             f"Доступные слои: 0-{max_layer}")
                        return None

            return layers
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректный формат слоев.\n"
                                           "Используйте: 0,1,2,3")
            return None