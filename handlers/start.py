from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes


START_TEXT = (
    "Привет! Это интерактивный спутник экскурсии «От посикунчиков до Пермских богов».\n\n"
    "Здесь ты пройдёшь 5 точек маршрута, ответишь на задания, соберёшь впечатления "
    "и в финале получишь свой «Паспорт пермяка».\n\n"
    "Нажми кнопку, чтобы начать."
)

HELP_TEXT = (
    "Я помогу пройти интерактивную экскурсию «От посикунчиков до Пермских богов».\n\n"
    "Как это работает:\n"
    "1. Нажми «Начать маршрут».\n"
    "2. Введи имя.\n"
    "3. Проходи точки экскурсии по порядку.\n"
    "4. Отвечай на короткие задания.\n"
    "5. В финале пройди квиз и получи «Паспорт пермяка».\n\n"
    "Если хочешь начать заново, используй команду /restart."
)


def start_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("Начать маршрут", callback_data="start_route")]]
    )


def reset_user_state(context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data.clear()
    context.user_data.update(
        {
            "name": None,
            "route_index": 0,
            "route_answers": {},
            "quiz_index": 0,
            "quiz_score": 0,
            "quiz_answers": {},
            "stage": "start",
        }
    )


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    reset_user_state(context)
    await update.message.reply_text(START_TEXT, reply_markup=start_keyboard())


async def restart_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await start_command(update, context)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(HELP_TEXT)


async def start_route_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    context.user_data.clear()
    context.user_data.update(
        {
            "name": None,
            "route_index": 0,
            "route_answers": {},
            "quiz_index": 0,
            "quiz_score": 0,
            "quiz_answers": {},
            "stage": "waiting_for_name",
        }
    )
    await query.message.reply_text("Как тебя зовут? Напиши имя одним сообщением.")


async def restart_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    reset_user_state(context)
    await query.message.reply_text(START_TEXT, reply_markup=start_keyboard())


async def help_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    await query.message.reply_text(HELP_TEXT)
