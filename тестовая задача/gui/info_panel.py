import tkinter as tk
from tkinter import ttk, scrolledtext
from utils.file_io import read_problem_from_file


class InfoPanel:
    def __init__(self, parent, main_app):
        self.parent = parent
        self.main_app = main_app
        self.setup_info_panel()

    def setup_info_panel(self):
        # Информация о задаче
        info_frame = ttk.LabelFrame(self.parent, text="ПОСТАНОВКА ЗАДАЧИ", style='Blue.TLabelframe')
        info_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Создаем текстовое поле
        self.info_text_widget = scrolledtext.ScrolledText(info_frame, height=8, width=60,
                                                          bg='#f0f8ff', fg='#0066cc',
                                                          font=('Courier', 10), wrap=tk.WORD, padx=10)
        self.info_text_widget.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Обновляем информацию при запуске
        self.update_problem_info()

    def update_problem_info(self):
        """Обновляет информацию о задаче из файла"""
        problem_data = read_problem_from_file()

        if problem_data:
            info_text = f"""
    УРАВНЕНИЕ:
    {problem_data['equation']}

    НАЧАЛЬНОЕ УСЛОВИЕ:
    {problem_data['initial_condition']}

    ГРАНИЧНЫЕ УСЛОВИЯ:
    {problem_data['left_boundary']}
    {problem_data['right_boundary']}

    ОБЛАСТЬ РЕШЕНИЯ:
    {problem_data['domain']}

    МЕТОД РЕШЕНИЯ:
    Явная разностная схема
    """
        else:
            info_text = """
    ФАЙЛ problem.txt НЕ НАЙДЕН

    Создайте файл problem.txt с постановкой задачи.
    """

        # Обновляем текст
        self.info_text_widget.config(state=tk.NORMAL)
        self.info_text_widget.delete(1.0, tk.END)
        self.info_text_widget.insert(tk.END, info_text)
        self.info_text_widget.config(state=tk.DISABLED)