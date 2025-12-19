import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
)
from config import TELEGRAM_BOT_TOKEN, BASE_CURRENCIES
from api_client import get_latest_rates
from utils import generate_chart
import os

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(curr, callback_data=f"rate_{curr}") for curr in BASE_CURRENCIES[:3]],
        [InlineKeyboardButton(curr, callback_data=f"rate_{curr}") for curr in BASE_CURRENCIES[3:]]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Привет! Я бот курсов валют.\n"
        "Выберите валюту или используйте команды:\n"
        "/rate <валюта> — курсы\n"
        "/convert <сумма> <из> to <в>\n"
        "/chart <из> <в> — график",
        reply_markup=reply_markup
    )

async def rate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Используйте: /rate <валюта>, например /rate USD")
        return
    base = context.args[0].upper()
    try:
        data = get_latest_rates(base)
        text = f"Курсы от {base}:\n"
        rates = data["rates"]
        for curr in sorted(rates.keys())[:10]:  # не более 10 валют
            text += f"{curr}: {rates[curr]:.4f}\n"
        await update.message.reply_text(text)
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")

async def convert_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if len(args) != 4 or args[2].lower() != "to":
        await update.message.reply_text("Используйте: /convert <сумма> <из> to <в>, например:\n/convert 100 USD to RUB")
        return
    try:
        amount = float(args[0])
        from_curr = args[1].upper()
        to_curr = args[3].upper()

        data = get_latest_rates(from_curr)
        rate = data["rates"].get(to_curr)
        if rate is None:
            await update.message.reply_text(f"Валюта {to_curr} не найдена.")
            return
        result = amount * rate
        await update.message.reply_text(f"✅ {amount} {from_curr} = {result:.2f} {to_curr}")
    except ValueError as e:
        await update.message.reply_text("Некорректная сумма.")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка конвертации: {e}")

async def chart_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 2:
        await update.message.reply_text("Используйте: /chart <из> <в>, например /chart USD RUB")
        return
    base = context.args[0].upper()
    target = context.args[1].upper()
    try:
        filename = generate_chart(base, target, days=7)
        await update.message.reply_photo(photo=open(filename, 'rb'))
        os.remove(filename)  # Удаляем файл после отправки
    except Exception as e:
        await update.message.reply_text(f" Не удалось построить график: {e}")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data.startswith("rate_"):
        base = query.data.replace("rate_", "")
        try:
            data = get_latest_rates(base)
            text = f"Курсы от {base}:\n"
            for curr in ["USD", "EUR", "RUB", "GBP", "JPY", "CHF", "CNY"]:
                if curr in data["rates"]:
                    text += f"{curr}: {data['rates'][curr]:.4f}\n"
            await query.edit_message_text(text=text)
        except Exception as e:
            await query.edit_message_text(f"❌ Ошибка: {e}")

def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("rate", rate_command))
    application.add_handler(CommandHandler("convert", convert_command))
    application.add_handler(CommandHandler("chart", chart_command))
    application.add_handler(CallbackQueryHandler(button_handler))

    print(" Бот запущен!")
    application.run_polling()

if __name__ == "__main__":
    main()