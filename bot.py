import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from matplotlib import rcParams
from PIL import Image, ImageDraw, ImageFont
import importlib
import common_analys as cmal
import pred
import advice as adv 
import re
from dateparser import parse
from dateparser.search import search_dates
from dateutil.relativedelta import relativedelta
from datetime import datetime
import nest_asyncio
import logging
import os
from io import BytesIO
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes



def escape_markdown_v2(text):
    escape_chars = r'[\_\\[\]\(\)\~\\>\#\+\-\=\|\{\}\.\!]'
    return re.sub(escape_chars, r'\\\g<0>', text)



def get_season_dates(year: int, season: str):
    seasons = {
        "весна": (datetime(year, 3, 1), datetime(year, 5, 31)),
        "лето": (datetime(year, 6, 1), datetime(year, 8, 31)),
        "осень": (datetime(year, 9, 1), datetime(year, 11, 30)),
        "зима": (datetime(year, 12, 1), datetime(year + 1, 2, 28))
    }
    return seasons.get(season.lower())

def parse_period(text: str):
    now = datetime.now()

    if "последний месяц" in text:
        end_date = now
        start_date = now - relativedelta(months=1)
        return start_date, end_date
    
    if "последний год" in text:
        end_date = now
        start_date = now - relativedelta(years=1)
        return start_date, end_date
    
    season_match = re.search(r"(весна|лето|осень|зима)\s(\d{4})", text.lower())
    if season_match:
        season, year = season_match.groups()
        year = int(year)
        season_dates = get_season_dates(year, season)
        if season_dates:
            return season_dates

    month_year_match = re.search(r"(\w+)\s(\d{4})", text.lower())
    if month_year_match:
        month_name, year = month_year_match.groups()
        month_date = parse(f"01 {month_name} {year}", settings={'DATE_ORDER': 'DMY'})
        if month_date:
            start_date = month_date
            end_date = month_date + relativedelta(months=1) - relativedelta(days=1)
            return start_date, end_date
        
    range_patterns = [
        r"с (\d{1,2}[./]\d{1,2}[./]\d{2,4}) по (\d{1,2}[./]\d{1,2}[./]\d{2,4})",
        r"(\d{1,2}[./]\d{1,2}[./]\d{2,4})-(\d{1,2}[./]\d{1,2}[./]\d{2,4})"
    ]
    
    for pattern in range_patterns:
        match = re.search(pattern, text)
        if match:
            start_str, end_str = match.groups()
            start_date = parse(start_str)
            end_date = parse(end_str)
            if start_date and end_date:
                return start_date, end_date

    parsed_dates = search_dates(text, settings={'PREFER_DATES_FROM': 'past'})
    
    if parsed_dates and len(parsed_dates) >= 2:
        return parsed_dates[0][1], parsed_dates[-1][1]
    
    return None, None


nest_asyncio.apply()

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


#INSERT YOUR OWN BOT TOKEN
TOKEN = ''




async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info("Команда /start вызвана")
    welcome_message = "Привет, я чат-бот, который поможет тебе разобраться в твоих финансах!\n\n👉Я могу проанализировать твои расходы и доходы.\n\n👉Дать пару советов как сэкономить хорошую часть твоих доходов.\n\n👉Предсказать твои будущие траты!\n\nНажми на кнопку, и мы начнём работать👻"
    keyboard = [[InlineKeyboardButton("Начать", callback_data='start')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = await update.message.reply_text(welcome_message, reply_markup=reply_markup)
    context.user_data['welcome_message_id'] = message.message_id



async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    logger.info(f"Button clicked: {query.data}")

    previous_message_id = context.user_data.get('welcome_message_id')
    if previous_message_id:
        try:
            await query.message.delete()
        except Exception as e:
            logger.error(f"Ошибка при удалении сообщения: {e}")

    if query.data == 'start':
        caption = (
            "К сожалению, я пока не могу получить доступ к твоим финансам напрямую😔\n\n"
            "🔆Скачай, пожалуйста, выгрузку по операциям из твоего мобильного банка в формате ***csv*** и пришли мне файл в чат🔆\n\n"
            "Чтобы получить файл со своими операциями:\n"
            "1️⃣Зайдите в ***личный кабинет Т\-банка*** на своём ***ПК***\n"
            "2️⃣Перейдите во вкладку ***Операции***\n"
            "3️⃣Найдите стрелочку для выгрузки Ваших операций\n"
            "4️⃣Скачайте файл в формате ***csv***\n"
        )

        photos = [
            InputMediaPhoto(open('inst1.jpg', 'rb'), caption=caption, parse_mode='MarkdownV2'),
            InputMediaPhoto(open('inst2.jpg', 'rb')),
            InputMediaPhoto(open('inst3.jpg', 'rb'))
        ]

        new_message = await query.message.reply_media_group(media=photos)
        context.user_data['previous_message_id'] = new_message[0].message_id


        
async def handle_post_upload(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    logger.info(f"Button clicked: {query.data}")

    previous_message_id = context.user_data.get('previous_message_id')
    if previous_message_id:
        try:
            await query.message.delete()
        except Exception as e:
            logger.error(f"Ошибка при удалении сообщения: {e}")

    if query.data == 'analytics':
        await query.message.reply_text("Введите период, за который Вам нужна аналитика👀")
        context.user_data['awaiting_date_period'] = True 

    elif query.data == 'save_money':
        df = context.user_data.get('df')
        filtered_data = adv.filter_by_date(df)
        advice_list = adv.advicing(filtered_data)
        advice_text = "\n\n".join(advice_list)
        new_message = await query.message.reply_text(escape_markdown_v2(advice_text), parse_mode='MarkdownV2')

        keyboard = [
            [InlineKeyboardButton("Назад", callback_data='back')],
            [InlineKeyboardButton("Выход", callback_data='exit')]
        ]
        await new_message.reply_text("Что вы хотите сделать дальше?", reply_markup=InlineKeyboardMarkup(keyboard))
        context.user_data['previous_message_id'] = new_message.message_id

    elif query.data == 'forecast':
        await query.message.reply_text("Введите количество месяцев, на которое вы хотите получить предсказание🤑")
        context.user_data['awaiting_forecast'] = True 

    elif query.data == 'exit':
        context.user_data.clear()
        await query.message.reply_text("Спасибо за использование бота! Если захотите продолжить, просто отправьте команду /start.")
        await start(update, context)


async def handle_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_input = update.message.text
    

    if context.user_data.get('awaiting_date_period'):
        start_date, end_date = parse_period(user_input)
        if start_date != None and end_date != None:
            context.user_data['start_date'] = start_date
            context.user_data['end_date'] = end_date
            context.user_data.pop('awaiting_date_period')  
            
            new_message = await update.message.reply_text("Вас понял, одну минуту!")

            df = context.user_data.get('df')

            start_date = context.user_data.get('start_date')
            end_date = context.user_data.get('end_date')

            processed_df = cmal.filter_data_by_date(start_date, end_date, df)

            results = []
            image_path = 'output_spend_days.png'
            cmal.spend_days(processed_df, image_path)
            results.append(image_path)

            f1 = 'output_all_spend1.png'
            f2 = 'output_all_spend2.png'
            f3 = 'output_all_spend3.png'
            count = cmal.all_spending(processed_df, f1, f2, f3)
            if count == 2:
                results.append(f1)
                results.append(f2)
            else:
                results.append(f3)

            ff1 = 'output_all_repl1.png'
            ff2 = 'output_all_repl2.png'
            ff3 = 'output_all_repl3.png'
            count_1 = cmal.all_repl(processed_df, ff1, ff2, ff3)
            if count_1 == 2:
                results.append(ff1)
                results.append(ff2)
            else:
                results.append(ff3)

            im_cash = 'cashback.png'
            cmal.cashback(processed_df, 'images/patrik.jpg', im_cash)
            results.append(im_cash)

            media = []
            for image_path in results:
                with open(image_path, 'rb') as image_file:
                    media.append(InputMediaPhoto(image_file))

            await update.message.reply_media_group(media=media)

            for im in results:
                os.remove(im)


            new_message = await update.message.reply_text("Надеюсь, моя аналитика вам поможет!🥺")

            keyboard = [
                [InlineKeyboardButton("Рассмотреть другой период", callback_data='another_period')],
                [InlineKeyboardButton("Назад", callback_data='back')],
                [InlineKeyboardButton("Выход", callback_data='exit')]
            ]
            await new_message.reply_text("Что вы хотите сделать дальше?", reply_markup=InlineKeyboardMarkup(keyboard))
            context.user_data['previous_message_id'] = new_message.message_id

        else:
            await update.message.reply_text("Не понял Вас, введите период по-другому, пожалуйста🥺")
    
    
    elif context.user_data.get('awaiting_forecast'):
        try:
            count = int(user_input)
            df = context.user_data.get('df')
            f1 = "forecast.png"
            pred.pred_spend(df, count, f1)
            with open(f1, 'rb') as image_file:
                new_message = await update.message.reply_photo(photo=image_file)
            os.remove(f1)
            context.user_data.pop('awaiting_forecast')  

            keyboard = [
                [InlineKeyboardButton("Рассмотреть другой период", callback_data='another_forecast_period')],
                [InlineKeyboardButton("Назад", callback_data='back')],
                [InlineKeyboardButton("Выход", callback_data='exit')]
            ]
            await new_message.reply_text("Что вы хотите сделать дальше?", reply_markup=InlineKeyboardMarkup(keyboard))
            context.user_data['previous_message_id'] = new_message.message_id
        except ValueError:
            await update.message.reply_text("Пожалуйста, введите корректное количество месяцев (целое число).")
    else:
        await handle_date_input(update, context)  



async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    file = update.message.document
    logger.info(f"Received document: {file.file_name}")

    chat_id = update.message.chat.id
    instruction_message_id = context.user_data.get('instruction_message_id')


    if instruction_message_id:
        for message_id in context.user_data.get('message_ids', []):
            if message_id <= instruction_message_id:
                try:
                    await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
                except Exception as e:
                    logger.error(f"Ошибка при удалении сообщения: {e}")

        context.user_data['message_ids'] = []

    try:
        file_obj = await file.get_file()
        file_data = await file_obj.download_as_bytearray()
        file_stream = BytesIO(file_data)
        file_stream.seek(0)

        df = pd.read_csv(file_stream, encoding='cp1251', sep=';')
        df = cmal.preparing(df)

        keyboard = [
            [InlineKeyboardButton("Моя аналитика", callback_data='analytics')],
            [InlineKeyboardButton("Хочу сэкономить", callback_data='save_money')],
            [InlineKeyboardButton("Сколько я потрачу?", callback_data='forecast')],
            [InlineKeyboardButton("Загрузить другой файл", callback_data='upload_new_file')],
            [InlineKeyboardButton("Выход", callback_data='exit')],
        ]
        new_message = await update.message.reply_text(f"Файл {file.file_name} успешно загружен и прочитан!", reply_markup=InlineKeyboardMarkup(keyboard))
        context.user_data['message_ids'] = [new_message.message_id]
        context.user_data['df'] = df
        context.user_data['filename'] = file.file_name

    except pd.errors.ParserError as e:
        logger.error(f"Ошибка при чтении файла: {e}")
        await update.message.reply_text(f"Файл {file.file_name} не может быть прочитан: проблема с форматом данных.")
    
    except UnicodeDecodeError as e:
        logger.error(f"Ошибка кодировки при чтении файла: {e}")
        await update.message.reply_text(f"Файл {file.file_name} не может быть прочитан: проблема с кодировкой. Попробуйте другой файл.")
    
    except Exception as e:
        logger.error(f"Ошибка при чтении файла: {e}")
        await update.message.reply_text(f"Файл {file.file_name} не подходит. Попробуйте загрузить другой файл.")




async def handle_followup_actions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    logger.info(f"Button clicked: {query.data}")

    chat_id = query.message.chat.id

    if query.data == 'another_period':
        previous_message_id = context.user_data.get('previous_message_id')
        if previous_message_id:
            try:
                await query.message.delete()
            except Exception as e:
                logger.error(f"Ошибка при удалении сообщения: {e}")

        await query.message.reply_text("Введите период, за который Вам нужна аналитика👀")
        context.user_data['awaiting_date_period'] = True

    elif query.data == 'another_forecast_period':
        previous_message_id = context.user_data.get('previous_message_id')
        if previous_message_id:
            try:
                await query.message.delete()
            except Exception as e:
                logger.error(f"Ошибка при удалении сообщения: {e}")

        await query.message.reply_text("Введите количество месяцев для нового прогноза🤑")
        context.user_data['awaiting_forecast'] = True

    elif query.data == 'back':
        previous_message_id = context.user_data.get('previous_message_id')
        if previous_message_id:
            try:
                await query.message.delete()
            except Exception as e:
                logger.error(f"Ошибка при удалении сообщения: {e}")
        keyboard = [
            [InlineKeyboardButton("Моя аналитика", callback_data='analytics')],
            [InlineKeyboardButton("Хочу сэкономить", callback_data='save_money')],
            [InlineKeyboardButton("Сколько я потрачу?", callback_data='forecast')],
            [InlineKeyboardButton("Загрузить другой файл", callback_data='upload_new_file')],
            [InlineKeyboardButton("Выход", callback_data='exit')],
        ]
        new_message = await query.message.reply_text("Выберите действие:", reply_markup=InlineKeyboardMarkup(keyboard))
        context.user_data['message_ids'] = [new_message.message_id]

    elif query.data == 'exit':
        context.user_data.clear()
        await query.message.reply_text("Спасибо за использование бота! Если захотите продолжить, просто отправьте команду /start.")
        await start(update, context)


async def handle_upload_new_file(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    logger.info(f"Button clicked: {query.data}")

    if query.data == 'upload_new_file':
        context.user_data.pop('df', None)
        context.user_data.pop('filename', None)
        caption = (
            "К сожалению, я пока не могу получить доступ к твоим финансам напрямую😔\n\n"
            "🔆Скачай, пожалуйста, выгрузку по операциям из твоего мобильного банка в формате ***csv*** и пришли мне файл в чат🔆\n\n"
            "Чтобы получить файл со своими операциями:\n"
            "1️⃣Зайдите в ***личный кабинет Т\-банка*** на своём ***ПК***\n"
            "2️⃣Перейдите во вкладку ***Операции***\n"
            "3️⃣Найдите стрелочку для выгрузки Ваших операций\n"
            "4️⃣Скачайте файл в формате ***csv***\n"
        )
        photos = [
            InputMediaPhoto(open('images/inst1.jpg', 'rb'), caption=caption, parse_mode='MarkdownV2'),
            InputMediaPhoto(open('images/inst2.jpg', 'rb')),
            InputMediaPhoto(open('images/inst3.jpg', 'rb'))
        ]

        await query.message.reply_media_group(media=photos)

async def main() -> None:
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))

    application.add_handler(CallbackQueryHandler(button_click, pattern='start'))
    application.add_handler(CallbackQueryHandler(handle_post_upload, pattern='analytics'))
    application.add_handler(CallbackQueryHandler(handle_post_upload, pattern='save_money'))
    application.add_handler(CallbackQueryHandler(handle_post_upload, pattern='forecast'))
    application.add_handler(CallbackQueryHandler(handle_post_upload, pattern='exit'))
    application.add_handler(CallbackQueryHandler(handle_followup_actions, pattern='another_period'))
    application.add_handler(CallbackQueryHandler(handle_followup_actions, pattern='another_forecast_period'))
    application.add_handler(CallbackQueryHandler(handle_followup_actions, pattern='back'))
    application.add_handler(CallbackQueryHandler(handle_upload_new_file, pattern='upload_new_file'))

    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_input))

    await application.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())


