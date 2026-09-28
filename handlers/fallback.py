from telegram import Update
from telegram.ext import ContextTypes

from handlers.route import handle_name


async def text_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    handled_as_name = await handle_name(update, context)
    if handled_as_name:
        return

    await update.message.reply_text(
        "Я здесь, чтобы провести тебя по маршруту. Используй кнопки ниже - так мы "
        "не потеряем точку экскурсии.\n\n"
        "Если кнопок нет, используй /restart."
    )


async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Такой команды нет. Чтобы начать заново, используй /restart."
    )
