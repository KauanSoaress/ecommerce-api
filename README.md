# ecommerce-api

A project to build an e-commerce API with FastAPI.

## How to run the project

### 1. Clone the repository

```bash
git clone https://github.com/KauanSoaress/ecommerce-api.git
cd ecommerce-api
```

### 2. Create a copy of `.env.example` and fill in the required environment variables

```bash
cp .env.example .env
```

### 3. Create the virtual environment and install the dependencies

This project uses **uv**.

```bash
uv venv
source .venv/bin/activate   # Linux/macOS
uv sync
```

### 4. Start the PostgreSQL container

```bash
docker compose up -d postgres
```

> Or, if you prefer to start the entire application:

```bash
docker compose up --build
```

### 5. Apply the database migrations

```bash
alembic upgrade head
```

### 6. Start the application

If you only started PostgreSQL in step 4:

```bash
docker compose up --build
```

If the application was already running, simply restart it:

```bash
docker compose restart ecommerce-api
```

## Project Structure

- `main.py` - Your FastAPI application
- `pyproject.toml` - Project dependencies

## Access DB docker
```bash
docker exec -it ecommerce-db psql -U postgres
```

## Generete a secret key
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## Create and apply a migration (After any table change)
```bash
alembic revision --autogenerate -m "message"

alembic upgrade head
```