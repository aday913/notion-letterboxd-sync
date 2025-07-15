# notion-letterboxd-sync

A terminal application to sync your Letterboxd watchlist with a Notion database.

## Features

- Scrapes your Letterboxd watchlist.
- Retrieves genres for each movie.
- Compares against existing entries in a Notion database.
- Automatically adds new watchlist movies to Notion.

## How it works

1. Fetches your Letterboxd watchlist by scraping your profile page.
2. For each movie, retrieves the list of genres.
3. Queries your Notion database for existing movie entries.
4. Adds any new movies to the Notion database with title, type (Movie), and genres.

## Requirements

- Python 3.7+
- Docker (for containerized execution)

## Installation

If you want to run the script locally, you can clone the repository and install the required dependencies:
```bash
git clone https://github.com/username/notion-letterboxd-sync.git
cd notion-letterboxd-sync
# Create a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt
```

If you prefer to run the script in a Docker container, you can skip the installation step and use the provided Dockerfile (see "Running with Docker" below).

## Environment Variables

- `NOTION_API_KEY`: Your Notion integration secret key.
- `NOTION_DATABASE_ID`: The ID of the target Notion database.
- `LETTERBOXD_USER`: Your Letterboxd username.
- `DEBUG` (optional): Set to "true" to enable debug logging ("false" by default).

## Usage

### Running locally

```bash
export NOTION_API_KEY="your_notion_api_key"
export NOTION_DATABASE_ID="your_database_id"
export LETTERBOXD_USER="your_letterboxd_username"
export DEBUG="false"

python main.py
```

### Running with Docker

Build the Docker image:

```bash
docker build -t notion-letterboxd-sync .
```

Run the container:

```bash
docker run --rm \
  -e NOTION_API_KEY="your_notion_api_key" \
  -e NOTION_DATABASE_ID="your_database_id" \
  -e LETTERBOXD_USER="your_letterboxd_username" \
  -e DEBUG="false" \
  notion-letterboxd-sync
```

Alternatively, you can also get the environment variables from a `.env` file by using the `--env-file` option:

```bash
docker run --rm \
  --env-file .env \
  notion-letterboxd-sync
```

## License

MIT License. See [LICENSE](LICENSE) for details.
