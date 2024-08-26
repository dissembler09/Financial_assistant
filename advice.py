#!/usr/bin/env python
# coding: utf-8

# In[7]:


import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import numpy as np
from matplotlib import rcParams
from PIL import Image, ImageDraw, ImageFont


# In[8]:


def preparing(data):
    data = data.copy()
    data = data[data['Статус'] == "OK"]
    data['Дата операции'] = pd.to_datetime(data['Дата операции'].str.split().str[0], format='%d.%m.%Y', errors='coerce')
    data['Дата платежа'] = pd.to_datetime(data['Дата платежа'].str.split().str[0], format='%d.%м.%Y', errors='coerce')
    
    numeric_columns = ['Сумма операции', 'Сумма платежа', 'Бонусы (включая кэшбэк)', 
                       'Округление на инвесткопилку', 'Сумма операции с округлением']
    
    for column in numeric_columns:
        data[column] = data[column].str.replace(',', '.', regex=False)
        data[column] = pd.to_numeric(data[column], errors='coerce')
    
    data['Пополнения'] = data['Сумма операции'].apply(lambda x: x if x > 0 else 0)
    data['Траты'] = data['Сумма операции'].apply(lambda x: -x if x < 0 else 0)

    return data



def filter_by_date(data):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)

    filtered_data = data[(data['Дата операции'] >= start_date) & (data['Дата операции'] <= end_date)]
    
    df = filtered_data.groupby('Категория', as_index=False).agg({'Траты' : 'sum'})
    total = df['Траты'].sum()
    df['percent'] = df['Траты'] / total * 100
    df = df[df['Траты'] > 0]
    df = df.nlargest(5, 'Траты')
    df = df.sort_values(by='Траты', ascending=False)
    df = df.rename(columns={'Категория':'category', 'Траты':'amount'})
    return df


def advicing(adv):
    res = []
    for index, row in adv.iterrows():
        cat = row['category']
        s = round(row['amount'], 2)
        perc = round(row['percent'])
        if cat != 'Переводы' and cat != 'Наличные' and cat != 'Услуги банка' and cat.lower().find('процент') == -1:
            if cat == 'Супермаркеты':
                message = '''💸В прошлом месяце в категории ***Супермаркеты*** Вы потратили ***{}*** рублей - это {}% от всех трат.\n\n\tВозможно, Вам стоит присмотреться к этой категории и снизить траты.\n\n\tРекомендую просмотреть хорошие предложения кэшбэка в категориях ***Супермаркеты*** и ***Доставка еды*** в приложении вашего банка.\n\n\tА также предлагаю вам выделить фиксированную сумму, которую Вы сможете тратить на эту категорию, например, за неделю!'''.format(s, perc)
            elif cat == 'Связь':
                message = '''💸В прошлом месяце в категории ***Связь*** Вы потратили ***{}*** рублей - это {}% от всех трат.\n\n\tВозможно, Вам стоит присмотреться к этой категории и снизить траты.\n\n\tПодключены ли вы к нашему мобильному оператору? Уверяю Вас, у нас самые **выгодные** тарифы и индивидуальные предложения при переносе номера!'''.format(s, perc)
            elif cat == 'Турагентства':
                message = '''💸В прошлом месяце в категории ***Турагенства*** Вы потратили ***{}*** рублей - это {}% от всех трат.\n\n\tНо кто же не любит отдыхать?\n\n\tПутешествия с нашей компанией это не просто отдых, но и ещё и **заработок**!\n\n\tСмотрите, как отдыхать и не считать деньги в приложении Вашего банка!'''.format(s, perc)
            else:
                message = '''💸В прошлом месяце в категории ***{}*** Вы потратили ***{}*** рублей - это {}% от всех трат.\n\n\tВозможно, Вам стоит присмотреться к этой категории и снизить траты.'''.format(cat, s, perc)
            res.append(message)
        if len(res) == 3:
            break
    message = '''👽Также советую Вам подключить функцию округления ваших трат.\n\n\tНапример, подключим округление до 100 рублей: с 10 покупок, например, на 370 рублей, Вы накопите ***300*** рублей!\n\n\tНезаметное округление поможет Вам заметить приятный ***бонус*** в конце месяца!'''
    res.append(message)
    message = '''👽Если у Вас всегда остаётся сумма на счету, не стесняйтесь перечислять её на вклад!\n\n\tМы предлагаем хорошие проценты и впоследсвии приятный пассивный ***заработок***!'''
    res.append(message)
    message = '''Подробнее о всех предложениях в мобильном приложении вашего банка.'''
    res.append(message)
    return res