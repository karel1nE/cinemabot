import aiohttp
import json
import typing as tp
from bs4 import BeautifulSoup
import re
import os


class NoSuchMovieException(Exception):
    pass


headers: dict[str, str] = {
    'X-API-KEY': os.getenv("X_API_KEY"),
    'Accept': '*/*',
    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
}

websites = [
    'kinogo', 'kinogo1', 'kinogoo', 'the-kinogo', 'kinogo-net',
    'kinogo-cc', 'kinoogo', 'hdrezka'
]


class MovieQuery:
    @staticmethod
    def _extract_website_name(url: str) -> str | None:
        pattern = re.compile(r'https?://(?:www\.)?([a-zA-Z0-9-]+)\.', re.IGNORECASE)
        match = pattern.match(url)
        if match:
            website_name = match.group(1)
            return website_name
        return None

    @staticmethod
    async def _kinopoisk_query(request_string: str) -> dict[str, tp.Any]:
        request_url = ("https://kinopoiskapiunofficial.tech/api/"
                       "v2.1/films/search-by-keyword?keyword=") + request_string + "&page=1"
        async with aiohttp.ClientSession() as session:
            async with session.get(request_url, headers=headers) as resp:
                response_body = json.loads(await resp.text())
                if len(response_body['films']) == 0:
                    raise NoSuchMovieException
                return response_body['films'][0]

    @staticmethod
    async def _get_links_by_query(search_query: str) -> list[str]:
        url = 'https://www.google.com/search'
        parameters = {'q': search_query + 'смотреть онлайн kinogo'}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=parameters, headers=headers) as resp:
                content = await resp.text()

        soup = BeautifulSoup(content, 'html.parser')

        search = soup.find(id='search')
        links = [tag['href'] for tag in search.findAll('a') if 'href' in tag.attrs.keys()]
        return links

    @staticmethod
    def _get_best_link(links: list[str]) -> str | None:
        for link in links:
            if MovieQuery._extract_website_name(link) in websites:
                return link

    @staticmethod
    async def get_movie_data(request_string: str) -> dict[str, tp.Any]:
        kinopoisk_data = await MovieQuery._kinopoisk_query(request_string)
        movie_links = await MovieQuery._get_links_by_query(kinopoisk_data['nameRu'])
        link = MovieQuery._get_best_link(movie_links)
        if link is None:
            raise NoSuchMovieException
        kinopoisk_data['watchLink'] = link
        return kinopoisk_data
