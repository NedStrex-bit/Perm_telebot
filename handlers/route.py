import random

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from data.route import ROUTE_POINTS


def route_keyboard(point_index: int) -> InlineKeyboardMarkup:
    point = ROUTE_POINTS[point_index]
    option_indexes = list(range(len(point["options"])))
    random.shuffle(option_indexes)
    buttons = [
        [InlineKeyboardButton(option, callback_data=f"route_answer:{point_index}:{i}")]
        for i in option_indexes
        for option in [point["options"][i]]
    ]
    return InlineKeyboardMarkup(buttons)


def next_route_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("К следующей точке", callback_data="next_route")]]
    )


def start_quiz_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("Начать квиз", callback_data="start_quiz")]]
    )


async def show_route_point(
    update: Update, context: ContextTypes.DEFAULT_TYPE, point_index: int | None = None
) -> None:
    if point_index is None:
        point_index = context.user_data.get("route_index", 0)

    point = ROUTE_POINTS[point_index]
    name = context.user_data.get("name", "Участник")
    text = (
        f"{point_index + 1}/5. {point['title']}\n\n"
        f"{point['intro'].format(name=name)}\n\n"
        f"{point['question']}"
    )

    target = update.callback_query.message if update.callback_query else update.message
    await target.reply_text(text, reply_markup=route_keyboard(point_index))


async def handle_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    if context.user_data.get("stage") != "waiting_for_name":
        return False

    name = update.message.text.strip()
    if len(name) > 40:
        await update.message.reply_text(
            "Давай короче, чтобы имя красиво поместилось в паспорт пермяка 🙂"
        )
        return True

    if not name:
        await update.message.reply_text("Напиши имя одним сообщением.")
        return True

    context.user_data["name"] = name
    context.user_data["stage"] = "route"
    context.user_data["route_index"] = 0

    await update.message.reply_text(f"Отлично, {name}! Начинаем маршрут.")
    await show_route_point(update, context, 0)
    return True


async def route_answer_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    _, point_index_raw, option_index_raw = query.data.split(":")
    point_index = int(point_index_raw)
    option_index = int(option_index_raw)

    if context.user_data.get("stage") != "route":
        await query.message.reply_text("Чтобы начать заново, используй /restart.")
        return

    current_index = context.user_data.get("route_index", 0)
    if point_index != current_index:
        await query.message.reply_text(
            "Эта точка уже не активна. Используй текущие кнопки ниже."
        )
        return

    point = ROUTE_POINTS[point_index]
    if point["id"] in context.user_data.get("route_answers", {}):
        await query.message.reply_text("Ответ уже принят. Нажми «К следующей точке».")
        return

    selected_option = point["options"][option_index]
    context.user_data.setdefault("route_answers", {})[point["id"]] = selected_option

    await query.message.reply_text(
        point["comment_after_answer"], reply_markup=next_route_keyboard()
    )


async def next_route_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if context.user_data.get("stage") != "route":
        await query.message.reply_text("Чтобы начать заново, используй /restart.")
        return

    current_index = context.user_data.get("route_index", 0)
    point_id = ROUTE_POINTS[current_index]["id"]
    if point_id not in context.user_data.get("route_answers", {}):
        await query.message.reply_text("Сначала выбери ответ на этой точке.")
        return

    next_index = current_index + 1
    if next_index >= len(ROUTE_POINTS):
        context.user_data["stage"] = "quiz_intro"
        name = context.user_data.get("name", "Участник")
        await query.message.reply_text(
            f"{name}, маршрут пройден! Теперь финальный квиз: 5 коротких вопросов, "
            "чтобы собрать все смыслы вместе.",
            reply_markup=start_quiz_keyboard(),
        )
        return

    context.user_data["route_index"] = next_index
    await show_route_point(update, context, next_index)
