# Tax Filing Assistant

A web app for filing a simplified Greek income tax return (φορολογική δήλωση) and getting AI-generated financial advice on it. Users sign up with their tax number (ΑΦΜ), submit their income, expenses and assets, see their past submissions, and ask GPT-4o for advice on any of them.

**Built:** June–July 2024. The commit history shows the project growing from a SQLite prototype to PostgreSQL, Docker and a CI/CD pipeline.
**Revisited:** October 2026. I fixed security and reliability issues and added automated tests (details below).

## Features

- **Accounts** with sign up and log in. Passwords are hashed with bcrypt, and sessions use JWT access tokens that expire after 10 minutes.
- **ΑΦΜ validation** checks the nine digits and the check digit.
- **Tax return form** (Greek UI) for income, deductible expenses, property and vehicles, with server-side validation.
- **Submission history**: every return a user files, newest first.
- **AI financial advice**: GPT-4o compares income with expenses and suggests improvements. Only the figures are sent to the model, never the user's name, ΑΦΜ or address.

## Tech stack

Python · FastAPI · Pydantic · PostgreSQL (psycopg2) · JWT (python-jose) · bcrypt (passlib) · OpenAI API · vanilla JavaScript, HTML and CSS · Docker / Docker Compose · GitHub Actions · pytest

## Run it

**With Docker** (app + PostgreSQL):

```bash
cp .env.example .env        # set SECRET_KEY, and OPENAI_API_KEY for the advice feature
docker compose up --build   # http://localhost:8000/login-page
```

**Without Docker** (Python 3.10+ and a running PostgreSQL):

```bash
pip install -r requirements.txt
cp .env.example .env        # set SECRET_KEY and DATABASE_URL
python main.py              # creates the tables on start-up
```

You can sign up with any valid ΑΦΜ; `090000045` is a valid test number.

## Tests and CI

```bash
docker compose up -d db
DATABASE_URL=postgresql://tax_assistant:1234@localhost:5432/tax_database pytest
```

The tests wipe the tables, so point them at a development database. They cover sign up and login, input validation, filing and reading back a return, blocking users from filing for someone else's ΑΦΜ, endpoints that require login, and checking that advice prompts contain no personal details. On every push, GitHub Actions runs them against a PostgreSQL service, then builds the Docker image and pushes it to Docker Hub.

## What changed in 2026

| Problem in the 2024 version | Fix |
|---|---|
| Any logged-in user could file a return under someone else's ΑΦΜ, overwriting that person's name and adding to their history | Returns can only be filed for the logged-in user's own ΑΦΜ (otherwise 403) |
| User-entered text and the AI's reply were inserted into the page as raw HTML (XSS) | User text is escaped, and AI output is sanitised with DOMPurify |
| The AI prompt included the user's ΑΦΜ, and the endpoint accepted any data from the browser | The browser sends only a submission ID. The server loads that submission, if it belongs to the user, and sends only the figures |
| Server logs recorded users' ΑΦΜs and full tax data, and the browser console printed login tokens | Logs record events only, with no personal data |
| After submitting a return, users were sent back to the login page, and refreshing a page logged them out (pages were loaded with `fetch` + `document.write`) | Pages load normally, and each page's JavaScript reads data from the protected API |
| CI ran `pytest`, but the repo had no tests, so the pipeline stopped at the test step | Added an API test suite, run against PostgreSQL in CI |
| `requirements.txt` was saved as UTF-16 and didn't list `bcrypt`, which passlib needs to hash passwords | Clean UTF-8 file with tested, pinned versions |
| Failed database writes were logged and ignored, so a failed save still returned "success"; a person and their submission were saved in separate transactions | Each submission is saved in a single transaction, and errors reach the client |
| CORS allowed any website; validation code in `models.py` never ran; the old SQLite files were unused | CORS removed (the front end is served by the same app), Pydantic validators in place, SQLite leftovers removed |
| `docker compose` relied on `DATABASE_URL` being set in `.env`, could start the app before the database was ready, and the image ran with `--reload` | Compose sets `DATABASE_URL` and waits for a database health check; the image runs without `--reload` |

## Limitations

This is a learning project, not a real tax service. The tax categories are simplified, tokens are kept in `localStorage`, and there are no refresh tokens. The database credentials in `docker-compose.yml` and the CI workflow are for local development and testing only. The AI advice is general information, not professional tax advice.
