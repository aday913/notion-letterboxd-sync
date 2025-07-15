import json
import logging

import requests

log = logging.getLogger(__name__)

def get_existing_notion_movies(api_key: str, database_id: str) -> list:
    all_movies = []

    # Prepare to fetch data from Notion
    has_more = True
    num_queries = 0
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    body_json = {}
    response = None

    try:
        while has_more:
            response = requests.api.post(
                f"https://api.notion.com/v1/databases/{database_id}/query",
                headers=headers,
                json=body_json
            )
            response.raise_for_status()

            formatted_response = response.json()

            # For every result, get the movie name
            for result in formatted_response["results"]:
                if not result.get('properties', {}).get('Name', {}).get('title'):
                    continue
                movie_title = result['properties']['Name']['title'][0]['plain_text']
                logging.debug(f"  Found movie: {movie_title}")
                all_movies.append(movie_title)

            # Handle pagination
            num_queries += 1
            has_more = bool(formatted_response.get("has_more", False))
            body_json["start_cursor"] = formatted_response.get("next_cursor", None)
    # Handle potential errors in the request
    except Exception as e:
        logging.error(f"Error fetching data from Notion: {e}")
        if response:
            logging.error(f"Response status code: {response.status_code}")
            logging.error(f"Response content: {response.content}")
        return []

    logging.info(f"Found {len(all_movies)} movies in the Notion database.")
    return all_movies


def put_movie_into_notion(json_data: dict, api_key: str):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(
            "https://api.notion.com/v1/pages",
            headers=headers,
            data=json.dumps(json_data, ensure_ascii=False, indent=4)
        )
        response.raise_for_status()
        logging.info("Movie successfully added to Notion.")
    except requests.RequestException as e:
        logging.error(f"Error adding movie to Notion: {e}")
        if response:
            logging.error(f"Response status code: {response.status_code}")
            logging.error(f"Response content: {response.content}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    _ = get_existing_notion_movies(, )

    _ = put_movie_into_notion()
