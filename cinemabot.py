import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram import F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.enums import ParseMode
from query_logic import MovieQuery, NoSuchMovieException
from movie_database import MovieDatabase
import os

logging.basicConfig(level=logging.INFO)

bot = Bot(token=os.getenv("BOT_TOKEN"),
          parse_mode=ParseMode.MARKDOWN)

dp = Dispatcher()
db = MovieDatabase()


@dp.message(Command("start"))
async def start_message(message: Message):
    await message.answer(
        """
👋 Привет! Меня зовут CinemaBot 🤖. Этот бот нужен для поиска фильмов 🎥. Вот возможные сценарии использования:

/help — команда для вывода справочной информации
/stats — вывод статистики по всем фильмам которые ты когда-либо искал- 
/history — вывод последних фильмов (до 10), которые ты искал

❗ И наконец просто введи название фильма и получи информацию о нём, а также ссылку для его просмотра ❗
        
        """
    )


@dp.message(Command("help"))
async def help_message(message: Message):
    await message.answer(
        """
/help — команда для вывода справочной информации
/stats — вывод статистики по всем фильмам которые ты когда-либо искал- 
/history — вывод последних фильмов (до 10), которые ты искал

❗ И наконец просто введи название фильма и получи информацию о нём, а также ссылку для его просмотра ❗
        """
    )


@dp.message(Command("history"))
async def history_message(message: Message):
    last_movies = db.get_last_movies(message.from_user.full_name)
    answer = "\n\n".join([f"{i + 1}. {row[3]}" for i, row in enumerate(last_movies)])
    await message.answer(f"Итак... твоя история поиска 🔎 выглядит так: \n\n{answer}")


@dp.message(Command("stats"))
async def stats_message(message: Message):
    movie_counts = db.count_movies(message.from_user.full_name)
    answer = ""
    for movie, count in movie_counts:
        answer += f"{movie}, {count} раз\n\n"
    await message.answer(f"Вот твоя статистика 🤓:\n\n{answer}")


@dp.message(F.text)
async def movie_searching(message: Message):
    negative_answer = f"Ох... Похоже такого фильма нету 😞"

    try:
        film_data = (await MovieQuery.get_movie_data(message.text))
    except NoSuchMovieException:
        await message.answer(negative_answer)
        return

    film_url = film_data.get('watchLink')
    image_url = film_data.get('posterUrlPreview')
    name = film_data.get('nameRu') if 'nameRu' in film_data else film_data.get('nameEn')
    year = film_data.get('year')
    description = film_data.get('description')
    rating = film_data.get('rating')

    if not image_url or not film_url or not name or not year or not description or not rating:
        await message.answer(negative_answer)
        return

    db.add_movie(message.from_user.full_name, name)
    await message.answer_photo(image_url,
                               f"""
*{name}*

{year}, Rating: {rating}

Описание. {description}

[Ссылка для просмотра]({film_url} 
""", disable_web_page_preview=True)


async def main():
    try:
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        db.close_connection()


if __name__ == "__main__":
    asyncio.run(main())
