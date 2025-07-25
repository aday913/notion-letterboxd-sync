#!/usr/bin/env python3

import logging
import os
import time

import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

log = logging.getLogger(__name__)


def get_letterboxd_watchlist(url: str) -> dict:
    watchlist = {}

    page = 1
    has_content = True
    while has_content:
        time.sleep(5)
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            target_url = f"{url}page/{page}" if page > 1 else url
            logging.debug(f"Fetching watchlist from: {target_url}")
            response = requests.get(target_url, headers=headers)
            response.raise_for_status()
        except requests.RequestException as e:
            logging.error(f"Error fetching data from {url}: {e}")
            return {}

        soup = BeautifulSoup(response.text, "html.parser")

        if len(soup.find_all("li", class_="poster-container")) == 0:
            logging.info("No more content found in the watchlist.")
            has_content = False
            break

        for li in soup.find_all("li", class_="poster-container"):

            div = li.find("div", class_="linked-film-poster")
            if div and div.has_attr("data-film-slug"):
                slug = div["data-film-slug"]
                logging.debug(f"  Found film slug: {slug}")
                watchlist[slug] = {}
            else:
                logging.warning("  No film slug found in the poster container.")
                has_content = False
                continue

            img = li.find("img")
            if img and img.has_attr("alt"):
                title = img["alt"]
                watchlist[slug]["title"] = title
            else:
                logging.warning("  No title found in the poster image.")
                has_content = False
                continue
        
        page += 1

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


def get_services_for_movie(movie: str) -> list:
    url = f"https://letterboxd.com/film/{movie}/"
    logging.debug(f"Fetching services for movie: {movie} from {url}")

    streaming_services = []
    with sync_playwright() as p:
        logging.debug("Launching Playwright browser...")
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(url, wait_until="load")
            time.sleep(5)  # Wait for the page to load completely

            logging.debug(f"Fetching content from {url} with BeautifulSoup")
            soup = BeautifulSoup(page.content(), "html.parser")

            for p_tag in soup.find_all("p", class_="service"):
                service_tag = p_tag.find("span", class_="name")
                if not service_tag:
                    continue

                service_name = service_tag.get_text(strip=True)

                for a_tag in p_tag.find_all("a"):
                    span = a_tag.find("span", class_="extended")
                    if span and span.get_text(strip=True).lower() == "play":
                        if service_name not in streaming_services:
                            logging.debug(f"Found streaming service: {service_name}")
                            streaming_services.append(service_name)
        except Exception as e:
            logging.error(f"Error fetching streaming services for movie {movie}: {e}")
        finally:
            browser.close()
    logging.info(f"Found {len(streaming_services)} streaming services for movie {movie}: {streaming_services}.")
    return streaming_services



if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    letterboxd_username = os.getenv("LETTERBOXD_USERNAME")
    if not letterboxd_username:
        logging.error("Please set the LETTERBOXD_USERNAME environment variable.")
        exit(1)

    titles = get_letterboxd_watchlist(f"https://letterboxd.com/{letterboxd_username}/watchlist/")

    all_services = set()
    all_genres = set()
    for slug, data in titles.items():
        logging.info(f"Movie: {data.get('title', 'Unknown')} (Slug: {slug})")
        genres = get_genres_for_movie(slug)
        services = get_services_for_movie(slug)
        if services:
            logging.info(f"  Streaming services: {', '.join(services)}")
            for service in services:
                all_services.add(service)
    logging.info(f"Total number of movies processed: {len(titles)}")
    for slug, data in titles.items():
        logging.info(f"  - {data.get('title', 'Unknown')} (Slug: {slug})")
    logging.info(f"Total unique streaming services found: {len(all_services)}") 
    for service in all_services:
        logging.info(f"  - {service}")
    logging.info(f"Total unique genres found: {len(all_genres)}")
    for genre in all_genres:
        logging.info(f"  - {genre}")
