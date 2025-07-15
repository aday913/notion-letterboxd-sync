#!/usr/bin/env python3

import logging
from typing import List, Tuple

import requests
from bs4 import BeautifulSoup

log = logging.getLogger(__name__)

def get_letterboxd_watchlist(url: str) -> dict:
    """
    Fetches the watchlist from a Letterboxd user profile. 

    Args:
        url (str): The URL of the Letterboxd user profile.

    Returns:
        Tuple[List[str], List[str]]: A tuple containing two lists:
            - A list of movie titles in the watchlist.
            - A list of corresponding movie slugs.
    """
    logging.info(f"Fetching watchlist from {url}")

    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"Error fetching data from {url}: {e}")
        return {}

    soup = BeautifulSoup(response.text, "html.parser")

    watchlist = {}
    for li in soup.find_all("li", class_="poster-container"):

        div = li.find("div", class_="linked-film-poster")
        if div and div.has_attr("data-film-slug"):
            slug = div["data-film-slug"]
            watchlist[slug] = {}
        else:
            continue

        img = li.find("img")
        if img and img.has_attr("alt"):
            title = img["alt"]
            watchlist[slug]["title"] = title
            logging.debug(f"  Found movie: {title}")

    logging.info(f"Found {len(watchlist)} items in the watchlist.")

    return watchlist


def get_genres_for_movie(movie: str) -> list:
    """
    Fetches genres for a movie from Letterboxd.

    Args:
        movies (string): A single movie slug.

    Returns:
        dict: A dictionary mapping movie titles to their genres.
    """
    url = f"https://letterboxd.com/film/{movie}/"
    logging.debug(f"Fetching genres for movie: {movie} from {url}")

    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"Error fetching data for movie {movie}: {e}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    genres = []
    for h3 in soup.find_all("h3"):
        if h3.get_text(strip=True).lower() == "genres":
            genre_div = h3.find_next_sibling("div", class_="text-sluglist")
            if genre_div:
                for a in genre_div.find_all("a", class_="text-slug"):
                    genres.append(a.get_text(strip=True))
            break

    return genres


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    titles = get_letterboxd_watchlist("https://letterboxd.com/aday913/watchlist/")
    print("Watchlist Titles:", titles)

    # genres = get_genres_for_movies(['thor-love-and-thunder'])
    # print("Genres for Movies:", genres)
