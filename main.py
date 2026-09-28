import asyncio
import logging
import os
import re
from pathlib import Path

from dotenv import load_dotenv
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

from handlers.fallback import text_message, unknown_command
from handlers.quiz import (
    next_quiz_callback,
    passport_callback,
    quiz_answer_callback,
    start_quiz_callback,
)
from handlers.route import next_route_callback, route_answer_callback
from handlers.start import (
    help_callback,
    help_command,
    restart_callback,
    restart_command,
    start_command,
    start_route_callback,
)


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

TOKEN_PATTERN = re.compile(r"^\d+:[A-Za-z0-9_-]{35,}$")


def build_application() -> Application:
    load_dotenv(Path(__file__).with_name(".env"))
    token = os.getenv("BOT_TOKEN", "").strip()
    if not token:
        raise RuntimeError("BOT_TOKEN не найден. Создайте .env по примеру .env.example.")
    if not TOKEN_PATTERN.fullmatch(token):
        raise RuntimeError(
            "BOT_TOKEN имеет неверный формат. Скопируйте полный токен из BotFather: "
            "сначала идут цифры, затем двоеточие и длинная строка, например "
            "123456789:AA..."
        )

    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("restart", restart_command))
    application.add_handler(CommandHandler("help", help_command))

    application.add_handler(CallbackQueryHandler(start_route_callback, pattern="^start_route$"))
    application.add_handler(CallbackQueryHandler(restart_callback, pattern="^restart$"))
    application.add_handler(CallbackQueryHandler(help_callback, pattern="^help$"))
    application.add_handler(
        CallbackQueryHandler(route_answer_callback, pattern=r"^route_answer:\d+:\d+$")
    )
    application.add_handler(CallbackQueryHandler(next_route_callback, pattern="^next_route$"))
    application.add_handler(CallbackQueryHandler(start_quiz_callback, pattern="^start_quiz$"))
    application.add_handler(
        CallbackQueryHandler(quiz_answer_callback, pattern=r"^quiz_answer:\d+:\d+$")
    )
    application.add_handler(CallbackQueryHandler(next_quiz_callback, pattern="^next_quiz$"))
    application.add_handler(CallbackQueryHandler(passport_callback, pattern="^get_passport$"))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_message))
    application.add_handler(MessageHandler(filters.COMMAND, unknown_command))

    return application


def main() -> None:
    application = build_application()

    try:
        asyncio.get_event_loop()
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())

    application.run_polling(allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    main()
