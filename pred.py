import warnings
import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib import rcParams
import seaborn as sns

# Подавление предупреждений
warnings.filterwarnings("ignore")


def scale_data(time_series):
    scaler = MinMaxScaler()
    scaled_data = scaler.fit_transform(time_series.values.reshape(-1, 1))
    return scaler, scaled_data

def forecast_spending_with_scaling(data, months_to_forecast):
    data = data.copy()
    df = data.rename(columns={'Дата операции':'date', 'Траты':'amount', 'Кэшбэк':'cashback', 'Категория':'category'})

    # Создание новых признаков
    df['month'] = df['date'].dt.month
    df['day_of_week'] = df['date'].dt.dayofweek
    df['is_weekend'] = df['day_of_week'].apply(lambda x: 1 if x >= 5 else 0)
    df['month_sin'] = np.sin(2 * np.pi * df['month']/12)
    df['month_cos'] = np.cos(2 * np.pi * df['month']/12)
    df['day_of_week_sin'] = np.sin(2 * np.pi * df['day_of_week']/7)
    df['day_of_week_cos'] = np.cos(2 * np.pi * df['day_of_week']/7)

    df['year_month'] = df['date'].dt.to_period('M')
    monthly_data = df.groupby(['year_month', 'category']).agg({'amount': 'sum'}).reset_index()

    categories = monthly_data['category'].unique()
    forecasted_results = []

    for category in categories:
        category_data = monthly_data[monthly_data['category'] == category]
        time_series = category_data.set_index('year_month')['amount']

        if len(time_series) < 3:
            continue

        try:
            # Масштабирование данных
            scaler, scaled_data = scale_data(time_series)
            time_series_scaled = pd.Series(scaled_data.flatten(), index=time_series.index)

            # Выбор модели в зависимости от объема данных
            if len(time_series_scaled) >= 12:
                model = SARIMAX(time_series_scaled, 
                                order=(1, 1, 1), 
                                seasonal_order=(1, 1, 1, 12), 
                                enforce_stationarity=False, 
                                enforce_invertibility=False)
            elif len(time_series_scaled) >= 6:
                model = ARIMA(time_series_scaled, order=(1, 1, 1))
            else:
                model = ARIMA(time_series_scaled, order=(0, 1, 1))

            # Финальный прогноз
            fitted_model = model.fit()
            forecast = fitted_model.get_forecast(steps=months_to_forecast)
            forecasted_sum_scaled = forecast.predicted_mean.sum()
            forecasted_sum = scaler.inverse_transform([[forecasted_sum_scaled]])[0][0]
            forecasted_sum = max(0, forecasted_sum)

            forecasted_results.append({'category': category, 'forecasted_amount': forecasted_sum})
        except Exception as e:
            continue

    result_df = pd.DataFrame(forecasted_results)
    return result_df




# In[77]:


def pred_spend(data, month, f1):
    data = data.copy()
    data = forecast_spending_with_scaling(data, month)
    data = data[data['forecasted_amount'] > 50]

    # Если категорий больше 15, оставляем только топ-15 по прогнозируемым тратам
    if len(data) > 15:
        data = data.nlargest(15, 'forecasted_amount')

    # Сортировка данных по убыванию для лучшей читаемости диаграммы
    data = data.sort_values(by='forecasted_amount', ascending=True)

    # Установка шрифта
    rcParams['font.family'] = 'DejaVu Sans'
    rcParams['font.size'] = 12

    # Построение горизонтальной гистограммы
    fig, ax = plt.subplots(figsize=(12, 8))
    colors = sns.color_palette("pink_r", len(data))

    bars = ax.barh(data['category'], data['forecasted_amount'], color=colors)

    # Добавление значений на столбцы
    for bar in bars:
        xval = bar.get_width()
        ax.text(xval + 5, bar.get_y() + bar.get_height()/2, int(xval), 
                ha='left', va='center', fontsize=12, color='black', fontweight='bold')

    # Добавление сетки
    ax.grid(True, axis='x', linestyle='--', alpha=0.7)

    # Добавление заголовка
    ax.set_title('Прогноз трат', fontsize=20, fontweight='bold', color='black', pad=20)

    # Настройка осей
    ax.set_xlabel('Сумма (в рублях)', fontsize=14, fontweight='bold', color='#49423d', labelpad=15)
    ax.set_ylabel('Категория', fontsize=14, fontweight='bold', color='#49423d', labelpad=15)

    # Настройка внешнего вида осей
    ax.tick_params(axis='x', colors='gray', labelsize=12)
    ax.tick_params(axis='y', colors='gray', labelsize=12)

    # Отключение верхней и правой рамок
    sns.despine(left=True, bottom=True)

    # Добавление пояснения внизу диаграммы
    if len(data) == 15:
        ax.text(0.5, -0.1, '\n\n\nВ остальных категориях траты минимальны', 
                ha='center', va='center', transform=ax.transAxes, 
                fontsize=15, color='#878787')

    # Сохранение изображения
    plt.savefig(f1, bbox_inches='tight', dpi=300)


