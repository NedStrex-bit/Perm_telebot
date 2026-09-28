import random

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from data.quiz import QUIZ_QUESTIONS
from services.passport import generate_passport


def quiz_keyboard(question_index: int) -> InlineKeyboardMarkup:
    question = QUIZ_QUESTIONS[question_index]
    option_indexes = list(range(len(question["options"])))
    random.shuffle(option_indexes)
    buttons = [
        [
            InlineKeyboardButton(
                option, callback_data=f"quiz_answer:{question_index}:{i}"
            )
        ]
        for i in option_indexes
        for option in [question["options"][i]]
    ]
    return InlineKeyboardMarkup(buttons)


def next_quiz_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("Следующий вопрос", callback_data="next_quiz")]]
    )


def passport_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("Получить паспорт пермяка", callback_data="get_passport")]]
    )


def final_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Пройти маршрут заново", callback_data="restart")],
            [InlineKeyboardButton("Помощь", callback_data="help")],
        ]
    )


async def show_quiz_question(
    update: Update, context: ContextTypes.DEFAULT_TYPE, question_index: int | None = None
) -> None:
    if question_index is None:
        question_index = context.user_data.get("quiz_index", 0)

    question = QUIZ_QUESTIONS[question_index]
    text = f"Вопрос {question_index + 1}/5\n\n{question['question']}"
    await update.callback_query.message.reply_text(
        text, reply_markup=quiz_keyboard(question_index)
    )


async def start_quiz_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    context.user_data["stage"] = "quiz"
    context.user_data["quiz_index"] = 0
    context.user_data["quiz_score"] = 0
    context.user_data["quiz_answers"] = {}
    await show_quiz_question(update, context, 0)


async def quiz_answer_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    _, question_index_raw, option_index_raw = query.data.split(":")
    question_index = int(question_index_raw)
    option_index = int(option_index_raw)

    if context.user_data.get("stage") != "quiz":
        await query.message.reply_text("Чтобы начать заново, используй /restart.")
        return

    current_index = context.user_data.get("quiz_index", 0)
    if question_index != current_index:
        await query.message.reply_text(
            "Этот вопрос уже не активен. Используй текущие кнопки ниже."
        )
        return

    if current_index in context.user_data.get("quiz_answers", {}):
        await query.message.reply_text("Ответ уже принят. Нажми «Следующий вопрос».")
        return

    question = QUIZ_QUESTIONS[question_index]
    is_correct = option_index == question["correct_option"]
    if not is_correct:
        await query.message.edit_reply_markup(reply_markup=None)
        await query.message.reply_text(
            f"Пока неверно. Подсказка: {question['hint']}\n\nПопробуй ещё раз.",
            reply_markup=quiz_keyboard(question_index),
        )
        return

    context.user_data["quiz_score"] = context.user_data.get("quiz_score", 0) + 1
    context.user_data.setdefault("quiz_answers", {})[question_index] = {
        "selected": question["options"][option_index],
        "is_correct": True,
    }

    await query.message.edit_reply_markup(reply_markup=None)
    await query.message.reply_text(
        question["comment"], reply_markup=next_quiz_keyboard()
    )


async def next_quiz_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if context.user_data.get("stage") != "quiz":
        await query.message.reply_text("Чтобы начать заново, используй /restart.")
        return

    current_index = context.user_data.get("quiz_index", 0)
    if current_index not in context.user_data.get("quiz_answers", {}):
        await query.message.reply_text("Сначала выбери ответ на этот вопрос.")
        return

    next_index = current_index + 1
    if next_index >= len(QUIZ_QUESTIONS):
        context.user_data["stage"] = "finished"
        name = context.user_data.get("name", "Участник")
        score = context.user_data.get("quiz_score", 0)
        await query.message.reply_text(
            f"Квиз завершён!\n\n{name}, твой результат: {score} из 5.",
            reply_markup=passport_keyboard(),
        )
        return

    context.user_data["quiz_index"] = next_index
    await show_quiz_question(update, context, next_index)


async def passport_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if context.user_data.get("stage") != "finished":
        await query.message.reply_text("Чтобы начать заново, используй /restart.")
        return

    name = context.user_data.get("name") or "Участник"
    score = context.user_data.get("quiz_score", 0)
    await query.message.reply_text(
        generate_passport(name, score), reply_markup=final_keyboard()
    )
