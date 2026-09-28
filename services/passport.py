from datetime import datetime
from zoneinfo import ZoneInfo


def get_status(score: int) -> str:
    if score <= 2:
        return "Начинающий путешественник по Парме"
    if score == 3:
        return "Знаток пермских символов"
    if score == 4:
        return "Хранитель пермских историй"
    return "Почётный проводник Пармы"


def generate_passport(name: str, score: int) -> str:
    date = datetime.now(ZoneInfo("Asia/Yekaterinburg")).strftime("%d.%m.%Y")
    status = get_status(score)

    return (
        "📜 Паспорт пермяка\n\n"
        f"Имя: {name}\n"
        "Маршрут: «От посикунчиков до Пермских богов»\n"
        f"Результат квиза: {score} из 5\n"
        f"Статус: {status}\n"
        f"Дата прохождения: {date}\n\n"
        "Этот паспорт подтверждает: ты прошёл маршрут, собрал ключевые символы "
        "Перми и стал частью истории, которую можно пересказать другим."
    )
