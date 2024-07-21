import os
import requests

from dotenv import load_dotenv


load_dotenv()


def search_movie_by_name(movie_title, limit):
    api_key = "EJ6PVGT-8B843P8-GZCJ00C-XB5XYWX"
    url = "https://api.kinopoisk.dev/v1.2/movie/search"
    headers = {
        "X-API-KEY": api_key
    }
    params = {
        "query": movie_title,
        "field": "name",
        "limit": limit
    }

    try:
        response = requests.get(url, headers = headers, params = params)
        response.raise_for_status()
        movie_data = response.json()

        if movie_data.get("docs"):
            return movie_data["docs"]
        else:
            return []

    except requests.exceptions.RequestException as e:
        print("Error fetching movie data:", e)
        return []

    except KeyError as e:
        print("Error: Unexpected JSON structure - missing key:", e)
        return []

    except IndexError as e:
        print("Error: Unexpected JSON structure - index error:", e)
        return []

    except Exception as e:
        print("Error:", e)
        return []


def search_movies_by_imdb_rating(min_rating, max_rating, limit):
    api_key = os.getenv("KPD_TOKEN")
    url = 'https://api.kinopoisk.dev/v1.4/movie'
    headers = {
        'accept': 'application/json',
        'X-API-KEY': api_key
    }
    imdb_rating = f'{min_rating}-{max_rating}'

    params = {
        'rating.imdb': imdb_rating,
        'limit': limit
    }

    try:
        response = requests.get(url, headers = headers, params = params)
        response.raise_for_status()
        movie_data = response.json()

        if movie_data.get("docs"):
            return movie_data["docs"]
        else:
            return []

    except requests.exceptions.RequestException as e:
        print("Error fetching movie data:", e)
        return []

    except KeyError as e:
        print("Error: Unexpected JSON structure - missing key:", e)
        return []

    except IndexError as e:
        print("Error: Unexpected JSON structure - index error:", e)
        return []

    except Exception as e:
        print("Error:", e)
        return []

# search_result = search_movies_by_imdb_rating(1, 3, 5)
# print(search_result)

def search_movies_by_genre(genre, limit, select_fields=None):
    api_key = os.getenv("KPD_TOKEN")

    url = "https://api.kinopoisk.dev/v1.4/movie"
    headers = {
        "Content-Type": "application/json",
        "X-API-KEY": api_key
    }
    params = {
        "genres.name": genre
    }

    if select_fields:
        params["selectFields"] = select_fields

    params["limit"] = limit

    try:
        response = requests.get(url, headers = headers, params = params)
        response.raise_for_status()
        movie_data = response.json()

        if 'error' in movie_data:
            return {'error': movie_data['error'], 'message': movie_data['message']}
        else:
            return movie_data

    except requests.exceptions.RequestException as e:
        print("Error fetching movie data:", e)
        return {'error': 500, 'message': str(e)}

    except Exception as e:
        print("Error:", e)
        return {'error': 500, 'message': str(e)}


# def search_movies_by_duration(min_duration, max_duration, limit=100):
#     api_key = "EJ6PVGT-8B843P8-GZCJ00C-XB5XYWX"
#     url = "https://api.kinopoisk.dev/v1.2/movie/search"
#     headers = {
#         "X-API-KEY": api_key
#     }
#     params = {
#         "field": "movieLength",
#         "limit": limit * 2  # Увеличиваем лимит, чтобы учесть фильтрацию вручную
#     }
#
#     try:
#         response = requests.get(url, headers=headers, params=params)
#         response.raise_for_status()
#         movie_data = response.json()
#         if movie_data.get("docs"):
#             # Фильтрация вручную по длительности
#             filtered_movies = [movie for movie in movie_data["docs"] if "movieLength" in movie and min_duration <= movie["movieLength"] <= max_duration]
#             return filtered_movies[:limit]
#         else:
#             return None
#     except requests.exceptions.RequestException as e:
#         print("Error fetching movie data:", e)
#         return None
#     except (KeyError, IndexError):
#         print("No movie data found")
#         return None
#
# # Пример использования функции
# print("Поиск фильмов по продолжительности:")
# movies_by_duration = search_movies_by_duration(40, 100, 100)
# if movies_by_duration:
#     for movie in movies_by_duration:
#         print(f"Название: {movie['name']}, Длительность: {movie['movieLength']} минут")
# else:
#     print("Фильмы не найдены")


# movies = search_movies_by_genre("боевик", 5)
# print(movies)
#
#
# movies = search_movies_by_rating(7.5, 8.5, 5)
# print(movies)
#
#
# movie_title = "Интерстеллар"
# movie_info = search_movie(movie_title, 5)
# print(movie_info)
