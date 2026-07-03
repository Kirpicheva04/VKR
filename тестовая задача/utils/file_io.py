import os
from tkinter import messagebox
import datetime
import random
import string


def read_problem_from_file(filename="problem.txt"):
    """Читает постановку задачи из файла"""
    try:
        # Проверяем существование файла
        if not os.path.exists(filename):
            raise FileNotFoundError(f"Файл {filename} не найден")

        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Удаляем пустые строки и лишние пробелы
        lines = [line.strip() for line in lines if line.strip()]

        if len(lines) >= 5:
            return {
                'equation': lines[0],
                'initial_condition': lines[1],
                'left_boundary': lines[2],
                'right_boundary': lines[3],
                'domain': lines[4]
            }
        else:
            raise ValueError("Недостаточно данных в файле")

    except FileNotFoundError:
        # Возвращаем значения по умолчанию если файл не найден
        return {
            'equation': "u't = γ²·u''xx + x·cos(t)",
            'initial_condition': "u(x,0) = -x² + 4x + 1",
            'left_boundary': "u(0,t) = 1",
            'right_boundary': "u(1,t) = 4",
            'domain': "x ∈ [0, 1], t ∈ [0, T]"
        }
    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка чтения файла: {str(e)}")
        return None

def generate_file_id():
    """Генерирует уникальный ID для файла"""
    # Вариант 1: с timestamp (дата и время)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    # Вариант 2: со случайными символами
    random_chars = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))

    # Комбинируем оба варианта для надежности
    return f"{timestamp}_{random_chars}"


def export_to_file(solver, step, filename=None):
    """Экспортирует данные расчета в файл"""
    try:
        # Создаем папку для результатов если ее нет
        results_dir = "results"
        if not os.path.exists(results_dir):
            os.makedirs(results_dir)

        # Генерируем уникальный ID
        file_id = generate_file_id()

        if filename is None:
            filename = f"Данные_расчета_шаг_{step}_id_{file_id}.txt"
        else:
            # Если передано имя файла, добавляем к нему ID
            name, ext = os.path.splitext(filename)
            filename = f"{name}_id_{file_id}{ext}"

        # Полный путь к файлу
        filepath = os.path.join(results_dir, filename)

        # Создаем список слоев с заданным шагом
        layers = list(range(0, len(solver.t), step))

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("ДАННЫЕ РАСЧЕТА УРАВНЕНИЯ ТЕПЛОПРОВОДНОСТИ\n")
            f.write("=" * 60 + "\n")

            f.write(f"Параметры расчета:\n")
            f.write(f"  Время T: {solver.T}\n")
            f.write(f"  Узлы по x (n): {solver.n}\n")
            f.write(f"  Слои по t (m): {solver.m}\n")
            f.write(f"  Шаг по x (h): {solver.h:.6f}\n")
            f.write(f"  Шаг по t (τ): {solver.tau:.6f}\n")
            f.write(f"Параметры модели:\n")
            f.write(f"  Коэффициент γ²: {solver.gamma ** 2:.6f}\n")
            f.write(f"Шаг вывода данных: {step}\n")
            f.write(f"ID расчета: {file_id}\n")
            f.write(f"Всего слоев: {len(solver.t)}\n")
            f.write(f"Экспортировано слоев: {len(layers)}\n")
            f.write(f"Дата экспорта: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n\n")

            for layer in layers:
                x, u_layer = solver.get_layer(layer)
                if x is not None:
                    f.write(f"Слой {layer} (t={solver.t[layer]:.6f}):\n")
                    for i, (x_val, temp) in enumerate(zip(x, u_layer)):
                        f.write(f"  x={x_val:.6f}: u={temp:.6f}\n")
                    f.write("\n")

        messagebox.showinfo("Успех", f"Данные успешно экспортированы в файл:\n{filename}")
        return filepath

    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка при экспорте данных: {str(e)}")
        return None

