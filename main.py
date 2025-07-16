#!/usr/bin/env python3

import logging
import os
import time

from utils.letterboxd import (
    get_letterboxd_watchlist,
    get_genres_for_movie,
    get_services_for_movie,
)
from utils.notion import get_existing_notion_movies, put_movie_into_notion


def main(api_key: str, database_id: str, letterboxd_user: str):

    # Fetch watchlist from Letterboxd
    watchlist_url = f"https://letterboxd.com/{letterboxd_user}/watchlist/"
    logging.info(f"Fetching watchlist from {watchlist_url}")
    watchlist = get_letterboxd_watchlist(watchlist_url)
    if not watchlist:
        logging.error("No watchlist found or an error occurred while fetching it.")
        return

    # Fetch genres for each movie in the watchlist
    logging.info("Fetching genres for movies in the watchlist...")
    all_genres = []
    all_services = []
    for slug, movie in watchlist.items():
        movie["genres"] = get_genres_for_movie(slug)
        movie["services"] = get_services_for_movie(slug)
        for genre in movie["genres"]:
            if genre not in all_genres:
                all_genres.append(genre)
        for service in movie["services"]:
            if service not in all_services:
                all_services.append(service)
        logging.debug(
            f"Movie: {movie['title']}, Genres: {movie['genres']}, Services: {movie['services']}"
        )
        time.sleep(3)  # Respectful delay to avoid rate limiting
    logging.info(f"Found unique genres: {all_genres}")
    logging.info(f"Found unique streaming services: {all_services}")

    # Generate title:slug mapping for Notion comparison
    title_slug_mapping = {movie["title"]: slug for slug, movie in watchlist.items()}

    # Fetch existing movies from Notion
    logging.info("Fetching existing movies from Notion...")
    existing_movies = get_existing_notion_movies(api_key, database_id)

    # If the existing movie is in the watchlist, remove it from the watchlist dict
    for movie in existing_movies:
        if movie not in title_slug_mapping:
            continue

        slug = title_slug_mapping[movie]
        logging.debug(
            f"Movie '{movie}' already exists in Notion, removing from watchlist."
        )
        del watchlist[slug]

    # If there are no movies left in the watchlist, exit
    if not watchlist:
        logging.info("No new movies to add to Notion.")
        return

    logging.info(f"Found {len(watchlist)} new movies to add to Notion.")

    for movie_slug in watchlist:
        title = watchlist[movie_slug]["title"]
        genres = watchlist[movie_slug]["genres"]

        data = {
            "parent": {"type": "database_id", "database_id": database_id},
            "properties": {
                "Name": {
                    "type": "title",
                    "title": [{"type": "text", "text": {"content": title}}],
                },
                "Type": {"type": "select", "select": {"name": "Movie"}},
                "Category": {
                    "type": "multi_select",
                    "multi_select": [{"name": genre} for genre in genres],
                },
            },
        }

        logging.info(f"  Adding movie '{title}' to Notion with genres {genres}...")

        # AVAILABLE SERVICES PERSONALLY
        available_services = ["Hulu", "Netflix", "Disney Plus", "HBO Max", "Apple TV+"]
        services = [
            service
            for service in watchlist[movie_slug]["services"]
            if service in available_services
        ]
        if services:
            logging.info(
                f"    Adding streaming services {services} for movie '{title}' to Notion."
            )
            data["properties"]["Source"] = {
                "type": "multi_select",
                "multi_select": [{"name": service} for service in services],
            }

        put_movie_into_notion(data, api_key)


if __name__ == "__main__":
    api_key = os.getenv("NOTION_API_KEY")
    database_id = os.getenv("NOTION_DATABASE_ID")
    letterboxd_user = os.getenv("LETTERBOXD_USER")
    debug = os.getenv("DEBUG", "false").lower() == "true"

    logging.basicConfig(
        level=logging.DEBUG if debug else logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    if not api_key or not database_id or not letterboxd_user:
        logging.error(
            "Missing environment variables. Please set NOTION_API_KEY, NOTION_DATABASE_ID, and LETTERBOXD_USER."
        )
        exit(1)

    main(api_key, database_id, letterboxd_user)
