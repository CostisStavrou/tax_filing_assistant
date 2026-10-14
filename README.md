# Tax Filing Assistant

A web app for filing a simplified Greek income tax return (φορολογική δήλωση) and getting AI-generated financial advice on it. Users sign up with their tax number (ΑΦΜ), submit their income, expenses and assets, see their past submissions, and ask GPT-4o for advice on any of them.

**Built:** June–July 2024. The commit history shows the project growing from a SQLite prototype to PostgreSQL, Docker and a CI/CD pipeline.

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
DATABASE_URL=postgresql://tax_assistant:1234@localhost:5433/tax_database pytest
```

The tests wipe the tables, so point them at a development database. They cover sign up and login, input validation, filing and reading back a return, blocking users from filing for someone else's ΑΦΜ, endpoints that require login, and checking that advice prompts contain no personal details. On every push, GitHub Actions runs them against a PostgreSQL service, then builds the Docker image. The image is pushed to Docker Hub when the `DOCKER_USERNAME` and `DOCKER_PASSWORD` secrets are set.

## Limitations

This is a learning project, not a real tax service. The tax categories are simplified, tokens are kept in `localStorage`, and there are no refresh tokens. The database credentials in `docker-compose.yml` and the CI workflow are for local development and testing only. The AI advice is general information, not professional tax advice.
