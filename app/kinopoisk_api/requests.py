import os
from dotenv import load_dotenv
from kinopoisk_dev import KinopoiskDev, MovieField, MovieParams,  PossValField
from kinopoisk_dev.model import MovieDocsResponseDto

# Загрузка переменных окружения из файла .env
load_dotenv()

# Получение токена из переменных окружения
token = os.getenv('KPD_TOKEN')


# def get_random_movie():
# 	client = KinopoiskDev(token = token)
#
# 	# Получение первой страницы с фильмами для определения общего количества фильмов
# 	params = MovieParams(keys = )
# 	response = client.movie.get_page(params = params, page = 1)
#
# 	# Получение общего количества фильмов
# 	total_movies = response.total
#
# 	# Генерация случайного номера страницы
# 	random_page = random.randint(1, (total_movies // response.per_page) + 1)
#
# 	# Получение фильмов с случайной страницы
# 	response = client.movie.get_page(params = params, page = random_page)
#
# 	# Выбор случайного фильма из списка
# 	random_movie = random.choice(response.docs)
#
# 	return random_movie
#
#
# # Пример использования функции get_random_movie
# random_movie = get_random_movie()
# print(f"Случайный фильм: {random_movie.name} (ID: {random_movie.id})")



# def get_movies_by_genre(genre: str, limit: int) -> MovieDocsResponseDto:
#     """
#     Получить информацию о фильмах по жанру.
#     :param genre: Жанр фильма
#     :param limit: Количество выводимых вариантов
#     :return: Список фильмов
#     """
#     kp = KinopoiskDev(token=token)
#
#     # Создаем параметры запроса для поиска фильмов по жанру
#     params = {
#         'genre': genre,
#         'limit': limit
#     }
#
#     # Вызываем метод для поиска фильмов по заданным параметрам
#     movies = kp.find_many_movie(params=params)
#
#     return movies
#
# genre = 'action'
# limit = 10

# movies = get_movies_by_genre(genre, limit)
# for movie in movies.items:
#     print(movie.title)


def get_movies_by_name(name: str, limit: int) -> MovieDocsResponseDto:
	"""
	Получить информацию о фильмах по названию.
	:param name: Название фильма
	:param limit: Количество выводимых вариантов
	:return: Список фильмов
	"""
	kp = KinopoiskDev(token = token)

	params = [
		MovieParams(keys = MovieField.NAME, value = name),
		MovieParams(keys = MovieField.LIMIT, value = limit),
	]

	items = kp.find_many_movie(params = params)

	if items.docs:
		for item in items.docs:
			print(f"Название: {item.name}")
			print(f"Год производства: {item.year or 'N/A'}")
			print(f"Жанр: {', '.join(genre.name for genre in item.genres) if item.genres else 'N/A'}")
			print(f"Описание: {item.description or 'N/A'}")
			print(f"Рейтинг: {item.rating.kp if item.rating and item.rating.kp is not None else 'N/A'}")
			if item.ageRating:
				print(f"Возрастной рейтинг: {item.ageRating}")
			if item.poster and item.poster.url:
				print(f"Постер: {item.poster.url}")
			if item.videos and item.videos.trailers:
				trailer = item.videos.trailers
				print(f"Трейлер: {trailer.url}")

			print("\n")
	else:
		print("Ничего не найдено.")

	return items


# actore prod
get_movies_by_name("начало", 5)
