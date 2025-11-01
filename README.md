# AINewsCurl

A Python-based scraper and summarizer for ETtoday news. It uses Selenium to load the latest news articles, parses content with BeautifulSoup, summarizes with a Large Language Model (Google Gemini via google-genai or a local Llama.cpp model via LangChain), and optionally records results to MySQL. A simple Flask API is provided, and a CLI entry point is available. Docker support and an example cron configuration are included.

## Overview
- Scrapes ETtoday "生活" focus page and filters recent news by relative time (e.g., 分鐘前/小時前).
- Extracts title, link, image, and content for each article.
- Summarizes article content using:
  - Google Gemini (default via google-genai), or
  - A local Llama.cpp model through LangChain (commented example kept).
- Outputs summaries to stdout; code includes hooks (commented) to write to MySQL and to maintain a rolling log CSV.
- Provides:
  - CLI runner: `python main.py`
  - Flask API: `python api.py` serving `GET /` to trigger a run
  - Dockerfile to containerize the API
  - Example crontab to run the CLI periodically

## Tech Stack
- Language: Python 3.11
- Frameworks/Libraries:
  - Flask (simple API)
  - Selenium (browser automation)
  - BeautifulSoup4 (HTML parsing)
  - LangChain (optional LLM wrapper; LlamaCpp integration)
  - google-genai (Gemini API client)
  - pandas (data handling)
  - SQLAlchemy + PyMySQL (optional MySQL persistence)
  - webdriver-manager (driver provisioning)
- Package manager: pip (requirements.txt)

## Requirements
- Python 3.11
- Google Chrome installed (for Selenium) when running locally
  - The code uses `webdriver-manager` to fetch a compatible ChromeDriver at runtime.
- Network access to ETtoday and Google APIs if using Gemini
- Optional: MySQL database (if you enable SQL writing)
- Docker (optional) if you prefer containerized API runtime

## Project Structure
```
AINewsCurl/
├─ Dockerfile                # Builds an image that runs the Flask API
├─ api.py                    # Flask API entry (GET / triggers a scrape+summarize)
├─ config.py                 # Configuration (currently hard-coded; see TODO)
├─ cron.log                  # Example log output for cron (if used)
├─ crontab                   # Example cron schedule to run main.py hourly
├─ debug.py                  # (Present; usage not wired up — see TODO)
├─ entrypoint.sh             # Entrypoint used in some Docker setups (not default)
├─ main.py                   # CLI entry to run a scrape+summarize once
├─ module/
│  └─ source.py              # Scraping, parsing, and output logic (ETToday class)
├─ LLM/
│  ├─ llm.py                 # Gemini client and optional local Llama.cpp wrapper
│  └─ prompt.py              # Prompt template for LangChain (optional path)
└─ requirements.txt          # Python dependencies
```

## Configuration and Environment Variables
Current state:
- `config.py` contains hard-coded values:
  - TOKEN (used as Gemini API key)
  - GROUP_ID (unused in current flow)
  - LOG_DIR (CSV log directory)
  - MySQL credentials: user, password, host, port, database
- `LLM/llm.py` sets `os.environ['GEMINI_API_KEY'] = TOKEN` automatically.

Recommendations (TODOs):
- TODO: Replace hard-coded secrets in `config.py` with environment variables and `.env` support (e.g., via `python-dotenv`). Suggested names:
  - GEMINI_API_KEY
  - GROUP_ID (if truly needed)
  - LOG_DIR
  - DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME
- TODO: Confirm whether MySQL persistence is desired (writes are currently commented in `module/source.py`).
- TODO: Confirm what `GROUP_ID` is for and wire it up or remove it.
- TODO: Clarify use of `debug.py` and delete or document.

## Setup (Local)
1. Ensure Python 3.11.
2. Create and activate a virtual environment:
   - macOS/Linux: `python3 -m venv .venv && source .venv/bin/activate`
   - Windows: `py -3.11 -m venv .venv && .venv\\Scripts\\activate`
3. Install dependencies:
   - `pip install -r requirements.txt`
4. Ensure Google Chrome is installed (for Selenium). On Linux, you can also rely on Docker (see below).
5. Prepare a data directory if you want to use CSV logging:
   - `mkdir -p data`
   - If using `news_cache` or history CSV, code expects `{LOG_DIR}/log.csv`. Initialize an empty CSV if needed.
6. Provide Gemini API key:
   - Current code reads TOKEN from `config.py` and assigns it to `GEMINI_API_KEY` at runtime.
   - Recommended: Set an environment variable `GEMINI_API_KEY` and modify `config.py` to load from env. See TODOs.
7. (Optional) MySQL:
   - Create the target database and table if you plan to enable `write_sql`.
   - Update credentials (prefer env vars) and uncomment calls in `module/source.py`.

## Running

### CLI (once)
- `python main.py`
  - Instantiates `ETToday()` and calls `news.output(scroll_count=3, chain=gemini)`.
  - Prints title and summary for each recent article.

### Flask API (development)
- `python api.py`
  - Starts the server on `http://0.0.0.0:5000/`
  - `GET /` triggers the same scrape+summarize routine and returns `curl finished...`

### Docker (API)
Build:
- `docker build -t ainewscurl:latest .`

Run:
- `docker run --rm -p 5000:5000 --name ainewscurl ainewscurl:latest`

Notes:
- Dockerfile installs Google Chrome and requirements, and runs `api.py` by default exposing port 5000.
- If you need environment variables inside the container (recommended for secrets), pass them with `-e`, e.g.:
  - `docker run -e GEMINI_API_KEY=... -p 5000:5000 ainewscurl:latest`
- `entrypoint.sh` is present but not used by the current Dockerfile CMD; it can be adapted if you switch to an ENTRYPOINT.

### Cron (example)
- `crontab` contains:
  - `0 * * * *  /usr/local/bin/python3.11 /app/main.py >> /var/log/cron.log 2>&1`
- In Docker, the cron setup is commented out in the Dockerfile. If you need it, uncomment the relevant lines and ensure `/var/log/cron.log` exists.

## Scripts and Key Functions
- CLI entry: `main.py`
- API entry: `api.py`
- Core scraping and processing:
  - `module/source.py`
    - `ETToday.get_recent_news_with_scrolling(scroll_count=3)`
    - `ETToday.output(scroll_count, chain)`
    - `news_detail(link_url)`
    - Optional SQL helpers: `write_sql`, `get_data`, `delete_data`
- LLMs:
  - `LLM/llm.py` → `gemini(context)` and `LargeLanguageModel(path)`
  - `LLM/prompt.py` → optional PromptTemplate content (used in commented example)

## Environment variables
Current code uses `config.py` constants, but the following env vars are recommended for production:
- GEMINI_API_KEY: Google Gemini API key (currently taken from `config.TOKEN`)
- LOG_DIR: path for CSV logs (default in code: `./data`)
- DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME: if enabling SQL output
- GROUP_ID: only if used by your downstream consumers (currently unused)

Because `config.py` currently hard-codes values, updating it to read from `os.environ` (with sensible defaults) is a TODO.

## Testing
- No automated tests were found in this repository.
- TODO: Add unit tests for:
  - Parsing functions (`news_detail`)
  - Filtering logic in `get_recent_news_with_scrolling`
  - LLM wrapper behavior (mock external API)
  - API route (`GET /`)

## Notes and Caveats
- A minor variable name issue is present in `news_parser`: it appends `externalLink` (camelCase) but the variable defined above is `external_link` (snake_case). This function is not used by the main flow but should be corrected if you enable it.
- `write_sql` and `delete_data` are provided but commented out at call sites; ensure your DB is prepared before enabling them.
- Ensure `LOG_DIR` exists if you intend to write CSV logs.
- Selenium runs a real Chrome browser. Headless mode is commented; you may enable `--headless` if desired.

## License
- No license file was found in the repository.
- TODO: Add a LICENSE file (e.g., MIT, Apache-2.0) to clarify usage and distribution rights.

## Changelog
- 2025-10-01: Initial README authored based on repository source inspection.
