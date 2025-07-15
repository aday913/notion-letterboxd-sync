#!/usr/bin/env python3

import logging

import requests
from bs4 import BeautifulSoup


def get_letterboxd_watchlist(url: str) -> list:
    """
    Fetches the watchlist from a Letterboxd user profile.

    Args:
        url (str): The URL of the Letterboxd user profile.

    Returns:
        list: A list of movie titles in the watchlist.
    """
    logging.info(f"Fetching watchlist from {url}")

    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"Error fetching data from {url}: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")

    watchlist = []
    for li in soup.find_all("li", class_="poster-container"):
        img = li.find("img")
        if img and img.has_attr("alt"):
            title = img["alt"]
            watchlist.append(title)
            logging.debug(f"  Found movie: {title}")

    logging.info(f"Found {len(watchlist)} items in the watchlist.")

    return watchlist


def get_services_for_movies(movies: list) -> dict:
    """
    Placeholder function to get services for movies.
    This function should be implemented to return a dictionary of movies and their streaming services.

    Args:
        movies (list): A list of movie titles.

    Returns:
        dict: A dictionary mapping movie titles to their streaming services.
    """
    # This is a placeholder implementation.
    # You would need to implement the actual logic to fetch services for each movie.
    return {movie: "Available on some service" for movie in movies}


def get_genres_for_movies(movies: list) -> dict:
    """
    Placeholder function to get genres for movies.
    This function should be implemented to return a dictionary of movies and their genres.

    Args:
        movies (list): A list of movie titles.

    Returns:
        dict: A dictionary mapping movie titles to their genres.
    """
    # This is a placeholder implementation.
    # You would need to implement the actual logic to fetch genres for each movie.
    return {movie: "Genre not specified" for movie in movies}


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    print(get_letterboxd_watchlist("https://letterboxd.com/aday913/watchlist/"))
