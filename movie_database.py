import sqlite3
from datetime import datetime
import typing as tp


class MovieDatabase:
    def __init__(self, db_path: str = 'movie_database.db') -> None:
        self.db_path = db_path
        self.connection = sqlite3.connect(db_path)
        self.create_table()

    def create_table(self):
        query = '''
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            datetime TEXT,
            film TEXT
        );
        '''
        with self.connection:
            self.connection.execute(query)

    def add_movie(self, username: str, film_name: str) -> None:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        query = "INSERT INTO movies (username, datetime, film) VALUES (?, ?, ?);"
        with self.connection:
            self.connection.execute(query, (username, now, film_name))

    def get_last_movies(self, username, limit: int = 10) -> list[tuple[tp.Any]]:
        query = "SELECT * FROM movies WHERE username=? ORDER BY datetime DESC LIMIT ?;"
        with self.connection:
            cursor = self.connection.execute(query, (username, limit))
            movies = cursor.fetchall()
            return movies

    def count_movies(self, username: str, limit: int = 10) -> list[tuple[str, int]]:
        query = '''
            SELECT film, COUNT(*) as count
            FROM movies
            WHERE username=?
            GROUP BY film
            ORDER BY count DESC
            LIMIT ?;
        '''
        with self.connection:
            cursor = self.connection.execute(query, (username, limit))
            counts = cursor.fetchall()
            return counts

    def backup(self, backup_path: str) -> None:
        with sqlite3.connect(self.db_path) as source:
            with sqlite3.connect(backup_path) as dest:
                source.backup(dest)

    def restore(self, backup_path: str) -> None:
        with sqlite3.connect(backup_path) as source:
            with sqlite3.connect(self.db_path) as dest:
                source.backup(dest)

    def close_connection(self) -> None:
        self.connection.close()
