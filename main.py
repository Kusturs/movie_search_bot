import os
import logging
import sys
import asyncio

from dotenv import load_dotenv
from telebot import StateMemoryStorage, TeleBot
from telebot.handler_backends import StatesGroup, State
from telebot.types import Message, BotCommand

import app.database.requests as rq
import app.database.models as md

import app.api as ap

load_dotenv()

state_storage = StateMemoryStorage()
bot = TeleBot(token=os.getenv('TG_TOKEN'), state_storage=state_storage)

DEFAULT_COMMANDS = (
    ('search_by_name', 'Поиск по названию'),
    ('search_by_rating', 'Поиск по рейтингу'),
    ('search_by_genre', 'Поиск по жанру'),
)


@bot.message_handler(commands=['start'])
def send_welcome(message: Message):
    asyncio.run(rq.set_user(message.from_user.id))
    text = 'Привет! Я бот для поиска фильмов. Напиши мне!'
    bot.send_message(message.from_user.id, text)


@bot.message_handler(commands=['search_by_name'])
def ask_for_movie_name(message: Message):
    bot.send_message(message.from_user.id, 'Введите название фильма:')
    bot.register_next_step_handler(message, ask_for_limit)


def ask_for_limit(message: Message):
    movie_name = message.text.strip()
    bot.send_message(message.from_user.id, 'Введите лимит количества результатов:')
    bot.register_next_step_handler(message, process_movie_search, movie_name)


def process_movie_search(message: Message, movie_name):
    limit = message.text.strip()

    if not limit.isdigit():
        bot.send_message(message.from_user.id, 'Лимит должен быть числом. Пожалуйста, введите снова:')
        bot.register_next_step_handler(message, process_movie_search, movie_name)
        return

    limit = int(limit)
    movies = ap.search_movie_by_name(movie_name, limit)

    if movies:
        for movie in movies:
            name = movie.get('name', 'N/A')
            description = movie.get('description', 'N/A')
            rating = movie.get('rating', 'N/A')
            year = movie.get('year', 'N/A')
            genres = ', '.join(movie.get('genres', []))
            poster = movie.get('poster', 'N/A')

            try:
                info = (
                    f"Название: {name}\n\n"
                    f"Год производства: {year}\n"
                    f"Жанры: {genres}\n\n"
                    f"Описание: {description}\n\n"
                    f"Рейтинг: {rating}\n"
                )
                bot.send_photo(message.chat.id, poster, caption=info)
            except Exception as e:
                continue
    else:
        bot.send_message(message.from_user.id, 'Фильмы не найдены.')


@bot.message_handler(commands = ['search_by_rating'])
def ask_for_rating(message: Message):
    bot.send_message(message.from_user.id, 'Введите минимальный рейтинг (от 0 до 10):')
    bot.register_next_step_handler(message, ask_for_max_rating)


def ask_for_max_rating(message: Message):
    try:
        min_rating = float(message.text)
        if min_rating < 0 or min_rating > 10:
            bot.send_message(message.chat.id, 'Неверный формат рейтинга. Введите число от 0 до 10:')
            bot.register_next_step_handler(message, ask_for_max_rating)
            return

        bot.send_message(message.chat.id, 'Введите максимальный рейтинг (от 0 до 10):')
        bot.register_next_step_handler(message, lambda m: ask_for_limit(m, min_rating))

    except ValueError:
        bot.send_message(message.chat.id, 'Неверный формат рейтинга. Введите число от 0 до 10:')
        bot.register_next_step_handler(message, ask_for_max_rating)


def ask_for_limit(message: Message, min_rating):
    try:
        max_rating = float(message.text)
        if max_rating < 0 or max_rating > 10 or max_rating < min_rating:
            bot.send_message(
                message.chat.id, 'Неверный формат рейтинга. Введите число от 0 до 10, больше чем минимальный рейтинг:'
                )
            bot.register_next_step_handler(message, lambda m: ask_for_limit(m, min_rating))
            return

        bot.send_message(message.chat.id, 'Введите количество фильмов для вывода:')
        bot.register_next_step_handler(message, lambda m: search_and_send_movies(m, min_rating, max_rating))

    except ValueError:
        bot.send_message(message.chat.id, 'Неверный формат рейтинга. Введите число от 0 до 10:')
        bot.register_next_step_handler(message, lambda m: ask_for_limit(m, min_rating))


# Функция для выполнения поиска и отправки результатов пользователю
def search_and_send_movies(message: Message, min_rating, max_rating):
    try:
        limit = int(message.text)
        if limit <= 0:
            bot.send_message(message.chat.id, 'Неверное количество фильмов. Введите положительное число:')
            bot.register_next_step_handler(message, lambda m: search_and_send_movies(m, min_rating, max_rating))
            return

        # Вызываем функцию для поиска фильмов по рейтингу IMDb
        search_result = ap.search_movies_by_imdb_rating(min_rating, max_rating, limit)

        if 'error' in search_result:
            bot.send_message(message.chat.id, f"Произошла ошибка: {search_result['message']}")
        else:
            for movie in search_result:
                name = movie.get('name', 'N/A')
                description = movie.get('description', 'N/A')
                rating = movie.get('rating', 'N/A')
                year = movie.get('year', 'N/A')
                genres = 's'
                poster = movie.get('poster', 'N/A')

                try:
                    info = (
                        f"Название: {name}\n\n"
                        f"Год производства: {year}\n"
                        f"Жанры: {genres}\n\n"
                        f"Описание: {description}\n\n"
                        f"Рейтинг: {rating}\n"
                    )
                    bot.send_photo(message.chat.id, poster, caption = info)
                except Exception as e:
                    continue
    except ValueError:
        bot.send_message(message.chat.id, 'Неверное количество фильмов. Введите положительное число:')
        bot.register_next_step_handler(message, lambda m: search_and_send_movies(m, min_rating, max_rating))


@bot.message_handler(commands=['search_by_genre'])
def ask_for_genre(message: Message):
    bot.send_message(message.from_user.id, 'Введите жанр:')
    bot.register_next_step_handler(message, ask_for_limit_genre)


@bot.message_handler(commands=['search_by_genre'])
def ask_for_genre(message: Message):
    bot.send_message(message.from_user.id, 'Введите жанр:')
    bot.register_next_step_handler(message, ask_for_limit_genre)


def ask_for_limit_genre(message: Message):
    genre = message.text.strip()
    bot.send_message(message.from_user.id, 'Введите лимит количества результатов:')
    bot.register_next_step_handler(message, process_genre_search, genre)


def process_genre_search(message: Message, genre):
    limit = message.text.strip()

    if not limit.isdigit():
        bot.send_message(message.from_user.id, 'Лимит должен быть числом. Пожалуйста, введите снова:')
        bot.register_next_step_handler(message, process_genre_search, genre)
        return

    limit = int(limit)
    movies = ap.search_movies_by_genre(genre, limit)

    if movies:
        for movie in movies:
            name = movie.get('name', 'N/A')
            description = movie.get('description', 'Нет описания' if not movie.get('description') else movie.get('description'))
            rating = movie.get('rating', 'N/A')
            year = movie.get('year', 'N/A')
            genres = ', '.join(movie.get('genres', []))
            poster = movie.get('poster', 'N/A')

            try:
                info = (
                    f"Название: {name}\n\n"
                    f"Год производства: {year}\n"
                    f"Жанры: {genres}\n\n"
                    f"Описание: {description}\n\n"
                    f"Рейтинг: {rating}\n"
                )
                bot.send_photo(message.chat.id, poster, caption=info)
            except Exception as e:
                continue
    else:
        bot.send_message(message.from_user.id, 'Фильмы не найдены.')


def is_valid_rating(rating):
    try:
        rating = float(rating)
        if 0.0 <= rating <= 10.0:
            return True
        return False
    except ValueError:
        return False


@bot.message_handler(commands=['history'])
def show_search_history(message: Message):
    pass


def main():
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(md.main())
    bot.set_my_commands([BotCommand(*cmd) for cmd in DEFAULT_COMMANDS])
    bot.polling()


if __name__ == '__main__':
    main()
