# Financial Assistant

## Описание проекта:
Чат-бот для анализа личных финансов в Telegram

## Цель проекта: 
Создание удобного и интерактивного чат-бота для анализа личных финансов, который помогает пользователям управлять своими доходами и расходами, а также прогнозирует будущие расходы и дает рекомендации по их оптимизации.

## Как запустить:
1. Получить доступ к файлам репозитория на своём ПК или в виртуальной среде (GitHub Codespaces)
2. При использовании виртуальной среды установить необходимые расширения (Python)
3. Установить зависимости: используйте команду **pip install -r requirements.txt** в терминале (командной строке)
4. Создать своего бота и получить **API Token** с помошью **BotFather в telegram**
5. Вставить полученный токен в файл **mytoken.txt**
6. Запустить файл **bot.py** в среде разработки или с помощью терминала (командной строки)
   
     6.1 При запуске через терминал, сначала используйте команду **cd**, чтобы перейти в папку, где находится файл **bot.py** (например, **cd C:\Users\ВашеИмя\Проект**).
   
     6.2 Затем используйте команду для запуска программы: **python bot.py**
8. Теперь с ботом можно взаимодействовать, перейдя по ссылке: [Запустить бота в Telegram](https://web.telegram.org/k/#@vm_smartcash_bot)

## Как взаимодействовать:
Сперва пользователь загружает файл со своими денежными операциями, затем общается с ботом посредством кнопок и естественного языка для получения необходимой информации.

## Основные функции:
- **Анализ финансовых данных**: Пользователь загружает выгрузку своих банковских операций в формате CSV, после чего бот анализирует данные и предоставляет визуализацию расходов и доходов по различным категориям.
- **Финансовые советы**: Бот предлагает рекомендации по оптимизации расходов на основе анализа данных, помогая пользователю более эффективно управлять своими финансами. Бот может рассказать о специальных предложениях, например, Т-банка, которые помогут пользователю сэкономить его средства.
- **Прогнозирование расходов**: Используя модели машинного обучения, бот прогнозирует будущие расходы на основе исторических данных. Пользователь может выбрать период для предсказания.
- **Распознавание дат и периодов**: Бот использует методы обработки естественного языка (NLP) для распознавания и интерпретации различных форматов дат и временных промежутков, включая последние месяцы, годы, сезоны и конкретные периоды.

## Технологии и библиотеки:
- **Python** — основной язык программирования.
- **Telegram Bot API** — для взаимодействия с пользователями через Telegram.
- **Pandas** — для обработки и анализа финансовых данных.
- **Matplotlib/Seaborn** — для визуализации данных.
- **Dateparser и Regex** — для обработки пользовательского ввода дат и распознавания шаблонов.
- **asyncio** — для асинхронного выполнения задач.
- **Machine Learning (ML)** - модели машинного обучения используются для прогнозирования расходов на основе исторических данных пользователя (конкретнее: ARIMA и SARIMAX).
- **Natural Language Processing (NLP)** - NLP методы применяются для распознавания и интерпретации вводимых пользователем дат и периодов.

## Логика работы:
1. При первом запуске бот приветствует пользователя и предлагает загрузить CSV-файл с финансовыми операциями.
2. После загрузки файла бот анализирует данные и предлагает пользователю выбрать дальнейшие действия: анализ расходов за определенный период, получение советов по экономии или прогнозирование будущих расходов с использованием МО.
3. Бот поддерживает обработку текстовых команд и взаимодействие через кнопки, что делает его удобным и простым в использовании.

## Преимущества:
- Интуитивно понятный интерфейс, который не требует от пользователя технических знаний.
- Возможность персонализированного анализа финансов.
- Использование машинного обучения для более точного прогнозирования будущих расходов.
- Визуализация данных, что помогает пользователю лучше понять свои финансовые привычки.
- Расширенные возможности NLP для точного распознавания временных интервалов.

## Перспективы развития:
- Расширение возможностей аналитики с учетом различных типов доходов и расходов.
- Добавление интеграции с банковскими API для автоматической загрузки данных.
- Улучшение моделей МО для более точных прогнозов и адаптации к изменениям в поведении пользователей.
- Переход к полному общению на естественном языке.

## **Скриншоты работы**
<details>
<summary>Нажмите, чтобы развернуть</summary>

![Screenshot 1](screens/v1.png)
![Screenshot 2](screens/v2.png)
![Screenshot 3](screens/v3.png)
![Screenshot 4](screens/v4.png)
![Screenshot 5](screens/v5.png)
![Screenshot 6](screens/v6.jpeg)
![Screenshot 7](screens/v7.jpeg)
![Screenshot 8](screens/v8.jpeg)
![Screenshot 9](screens/v9.jpeg)
![Screenshot 10](screens/v10.jpeg)
![Screenshot 11](screens/v11.jpeg)
![Screenshot 12](screens/v12.png)
![Screenshot 13](screens/v13.png)
![Screenshot 14](screens/v14.png)
![Screenshot 15](screens/v15.jpg)

</details>
