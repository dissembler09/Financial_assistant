import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import numpy as np
from matplotlib import rcParams
from PIL import Image, ImageDraw, ImageFont


def preparing(data):
    # Создаем копию данных, чтобы не изменять оригинал
    data = data.copy()
    
    # Фильтруем данные по статусу
    data = data[data['Статус'] == "OK"]
    
    # Убедимся, что колонки с датами содержат строки, прежде чем применять строковые методы
    if data['Дата операции'].dtype != 'O':
        data['Дата операции'] = data['Дата операции'].astype(str)
    if data['Дата платежа'].dtype != 'O':
        data['Дата платежа'] = data['Дата платежа'].astype(str)

    # Преобразуем даты
    data['Дата операции'] = pd.to_datetime(data['Дата операции'].str.split().str[0], format='%d.%m.%Y', errors='coerce')
    data['Дата платежа'] = pd.to_datetime(data['Дата платежа'].str.split().str[0], format='%d.%m.%Y', errors='coerce')

    # Преобразование числовых колонок (сначала заменяем запятые на точки)
    numeric_columns = ['Сумма операции', 'Сумма платежа', 'Бонусы (включая кэшбэк)', 
                       'Округление на инвесткопилку', 'Сумма операции с округлением']
    
    for column in numeric_columns:
        data[column] = data[column].str.replace(',', '.', regex=False)
        data[column] = pd.to_numeric(data[column], errors='coerce')
    
    # Отдельные колонки для пополнений и трат
    data['Пополнения'] = data['Сумма операции'].apply(lambda x: x if x > 0 else 0)
    data['Траты'] = data['Сумма операции'].apply(lambda x: -x if x < 0 else 0)

    return data


def filter_data_by_date(start_date, end_date, data):
    
    filtered_data = data[(data['Дата операции'] >= start_date) & (data['Дата операции'] <= end_date)]
    return filtered_data


# In[3]:


def spend_days(data, filename):

    # Группировка данных и вычисление средних трат
    avg_spending = data.groupby('Категория')['Траты'].mean().sort_values(ascending=False).reset_index()

    # Удаление строк с нулевыми значениями
    avg_spending = avg_spending[avg_spending['Траты'] > 0]

    # Округление значений до целых
    avg_spending['Траты'] = avg_spending['Траты'].round(0).astype(int)

    # Определение цветов градиента
    start_color = np.array([9/255, 174/255, 134/255])  # #09AE86
    end_color = np.array([1.0, 1.0, 1.0])               # #FFFFFF (белый)

    # Создание градиента
    gradient_colors = [start_color + (end_color - start_color) * i / (len(avg_spending) - 1) for i in range(len(avg_spending))]

    # Вычисление размера фигуры на основе количества строк
    num_rows = len(avg_spending) + 1  # +1 для заголовка
    row_height = 0.6  # Высота каждой строки
    fig_height = (num_rows * row_height) / 1.3  # +1 для заголовка таблицы
    fig_width = 8  # Ширина фигуры (можно настроить по желанию)

    # Настройка графика
    plt.figure(figsize=(fig_width, fig_height)) 
    plt.title('Средние траты по категориям (в день)', fontsize=16, fontweight='bold', fontname='Arial')
    plt.axis('tight')
    plt.axis('off')

    # Создание таблицы
    table = plt.table(cellText=avg_spending.values,
                      colLabels=['Категория', 'Средние траты, руб.'],
                      cellLoc='center',
                      loc='center')

    # Настройка стиля таблицы
    table.auto_set_font_size(False)
    table.set_fontsize(12)

    # Увеличение высоты строк и уменьшение ширины столбцов
    table.scale(1.5, 2.0)  # Увеличиваем высоту строк (второй параметр) 

    # Применение цвета к ячейкам
    for i in range(len(avg_spending)):
        for j in range(len(avg_spending.columns)):
            # Установка цвета ячейки
            table[(i + 1, j)].set_facecolor(gradient_colors[i])

            # Выравнивание текста по левому краю для первого столбца
            if j == 0:  # Для столбца "Категория"
                table[(i + 1, j)].set_text_props(ha='left', fontweight='bold')  # Выровнять по левому краю и сделать жирным
            else:  # Для столбца "Средние траты"
                table[(i + 1, j)].set_text_props(ha='center')  # Выровнять по центру

    # Установка жирного шрифта для заголовков и увеличение размера шрифта
    for j in range(len(avg_spending.columns)):
        cell = table[(0, j)]
        cell.set_fontsize(14)  # Увеличиваем размер шрифта заголовков
        cell.set_text_props(fontweight='bold')

    # Установка фиксированной ширины для столбцов
    table.auto_set_column_width([0, 1])  # Установка автоматической ширины для обоих столбцов
    table[(0, 0)].set_width(0.3)  # Уменьшаем ширину первого столбца
    table[(0, 1)].set_width(0.2)  # Уменьшаем ширину второго столбца

    # Сохранение таблицы как изображение
    plt.savefig(filename, bbox_inches='tight', dpi=300)


# In[10]:


def combine_small_categories(data, threshold, oper):
    category_spending = data.groupby('Категория')[oper].sum()
    total_spending = category_spending.sum()
    small_categories = category_spending[category_spending / total_spending < threshold].index
    
    data_copy = data.copy()
    data_copy['Категория'] = data_copy['Категория'].replace(small_categories, 'Прочее')
    
    return data_copy

def all_spending(data, f1, f2, f3):
    rcParams['font.family'] = 'Benbow'

    category_spending = data.groupby('Категория')['Траты'].sum()
    total_spending = category_spending.sum()
    # Находим крупнейшую категорию
    largest_category = category_spending.idxmax()
    largest_category_share = category_spending.max() / total_spending

    # Яркая фиолетовая палитра
    color_palette = ['#5C4D7A', '#8C6BB1', '#A45DB7', '#D54F82', '#B03B71', '#DA7C93', '#9B8A3D', '#CFA6D9', '#E2C6E5', '#EAB8D1']

    hold = 0.05
    if largest_category_share > 0.5 or len(category_spending) > 16:
        if len(category_spending) > 16:
            hold = 0.08
        data_combined = combine_small_categories(data, hold, oper="Траты")

        # Круговая диаграмма с объединением малых категорий
        plt.figure(figsize=(10, 8))
        sns.set(style="whitegrid")

        category_spending_combined = data_combined.groupby('Категория')['Траты'].sum()
        ttt = category_spending_combined.sum()
        category_spending_combined = category_spending_combined[category_spending_combined / ttt > 0.008]

        wedges, texts, autotexts = plt.pie(category_spending_combined, 
                                            autopct='%1.1f%%', 
                                            startangle=140, 
                                            colors=color_palette)

        plt.setp(autotexts, size=12, weight="bold", color="white")
        plt.legend(wedges, category_spending_combined.index, title="Категории", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
        plt.title('Распределение трат по категориям', fontsize=16, fontweight='bold')
        plt.axis('equal')
        plt.tight_layout()

        # Сохранение диаграммы
        plt.savefig(f1, bbox_inches='tight')

        # Диаграмма по тратам без крупнейшей категории
        plt.figure(figsize=(10, 8))
        without_largest = data[data['Категория'] != largest_category]
        without_largest_spending = without_largest.groupby('Категория')['Траты'].sum()
        sss = without_largest_spending.sum()
        without_largest_spending = without_largest_spending[without_largest_spending / sss > 0.008]

        without_largest_percentage = (without_largest_spending / total_spending) * 100

        bars = plt.barh(without_largest_spending.index, without_largest_spending, color=color_palette)

        for bar, percent in zip(bars, without_largest_percentage):
            plt.text(bar.get_width(), bar.get_y() + bar.get_height()/2, f'{percent:.1f}%', 
                     va='center', ha='left', color='black', fontsize=10)

        plt.title(f'Траты без категории "{largest_category}"', fontsize=16, fontweight='bold')
        plt.xlabel('Сумма трат')
        plt.ylabel('Категории')
        plt.tight_layout()

        plt.savefig(f2, bbox_inches='tight')
        return 2
    else:
        category_spending = category_spending[category_spending > 0.008]
        plt.figure(figsize=(10, 8))
        sns.set(style="whitegrid")

        wedges, texts, autotexts = plt.pie(category_spending, 
                                            autopct='%1.1f%%', 
                                            startangle=140, 
                                            colors=color_palette)

        plt.setp(autotexts, size=12, weight="bold", color="white")
        plt.legend(wedges, category_spending.index, title="Категории", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
        plt.title('Распределение трат по категориям', fontsize=16, fontweight='bold')
        plt.axis('equal')
        plt.tight_layout()

        # Сохранение диаграммы
        plt.savefig(f3, bbox_inches='tight')
        return 1

def all_repl(data, f1, f2, f3):
    rcParams['font.family'] = 'Benbow'

    df = data.copy()
    df.loc[df['Категория'] == 'Пополнения', 'Категория'] = df['Категория'] + ' - ' + df['Описание']

    category_repl = df.groupby('Категория')['Пополнения'].sum()
    total_repl = category_repl.sum()

    largest_category_repl = category_repl.idxmax()
    largest_category_repl_share = category_repl.max() / total_repl

    # Цветовая палитра синие оттенки
    color_palette = sns.blend_palette(["lightblue", "darkblue"], n_colors=12)

    # Проверяем, занимает ли крупнейшая категория более 60%
    if largest_category_repl_share > 0.5:
        data_combined_repl = combine_small_categories(df, 0.06, oper='Пополнения')

        # Круговая диаграмма с объединением малых категорий
        plt.figure(figsize=(10, 8))
        sns.set(style="whitegrid")

        category_spending_combined_repl = data_combined_repl.groupby('Категория')['Пополнения'].sum()

        wedges, texts, autotexts = plt.pie(category_spending_combined_repl, 
                                            autopct='%1.1f%%', 
                                            startangle=140, 
                                            colors=color_palette)

        plt.setp(autotexts, size=12, weight="bold", color="white")
        plt.legend(wedges, category_spending_combined_repl.index, title="Категории", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
        plt.title('Распределение пополнений по категориям', fontsize=16, fontweight='bold')
        plt.axis('equal')
        plt.tight_layout()

       
        plt.savefig(f1, bbox_inches='tight')
        
        plt.figure(figsize=(10, 8))
        without_largest_repl = df[df['Категория'] != largest_category_repl]
        without_largest_spending_repl = without_largest_repl.groupby('Категория')['Пополнения'].sum()

        without_largest_percentage_repl = (without_largest_spending_repl / total_repl) * 100
        filtered_spending_repl = without_largest_spending_repl[without_largest_percentage_repl > 0.1]
        filtered_percentage_repl = without_largest_percentage_repl[without_largest_percentage_repl > 0.1]

        bars = plt.barh(filtered_spending_repl.index, filtered_spending_repl, color=color_palette)

        for bar, percent in zip(bars, filtered_percentage_repl):
            plt.text(bar.get_width(), bar.get_y() + bar.get_height()/2, f'{percent:.1f}%', 
                     va='center', ha='left', color='black', fontsize=10)

        plt.title(f'Пополнения без категории "{largest_category_repl}"', fontsize=16, fontweight='bold')
        plt.xlabel('Сумма пополнений')
        plt.ylabel('Категории')
        plt.tight_layout()

        # Сохранение диаграммы
        plt.savefig(f2, bbox_inches='tight')
        return 2

    else:
        plt.figure(figsize=(10, 8))
        sns.set(style="whitegrid")

        wedges, texts, autotexts = plt.pie(category_repl, 
                                            autopct='%1.1f%%', 
                                            startangle=140, 
                                            colors=color_palette)

        plt.setp(autotexts, size=12, weight="bold", color="white")
        plt.legend(wedges, category_repl.index, title="Категории", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
        plt.title('Распределение пополнений по категориям', fontsize=16, fontweight='bold')
        plt.axis('equal')
        plt.tight_layout()

        
        plt.savefig(f3, bbox_inches='tight')
        return 1


def cashback(data, image_path, output_path):
    cash = data['Кэшбэк'].sum()

    text = str(cash) + ' РУБ!!!'
    image = Image.open(image_path)
    
    # Определяем размеры изображения
    width, height = image.size

    font_size = 50  # Увеличьте размер шрифта по вашему желанию
    font_path = "C:/Windows/Fonts/arialbd.ttf"  # Путь к жирному шрифту Arial
    font = ImageFont.truetype(font_path, font_size)

    # Создаем объект для рисования
    draw = ImageDraw.Draw(image)

    # Вычисляем размеры текста
    text_bbox = draw.textbbox((0, 0), text, font=font)  # Получаем границы текста
    text_width = text_bbox[2] - text_bbox[0]  # Ширина
    text_height = text_bbox[3] - text_bbox[1]  # Высота

    # Определяем позицию текста (по центру под изображением)
    text_x = (width - text_width) / 2
    text_y = height

    # Создаем новое изображение с дополнительным пространством для текста
    new_image = Image.new('RGB', (width, height + text_height + 40), (255, 255, 255))  # Добавляем немного отступа
    new_image.paste(image, (0, 0))

    # Добавляем текст на новое изображение
    draw = ImageDraw.Draw(new_image)
    draw.text((text_x, height - 80), text, font=font, fill="black")  # Небольшой отступ сверху от текста


    new_image.save(output_path)