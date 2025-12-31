# ===== 設定 =====
PYTHON=.venv/bin/python
UVICORN=.venv/bin/uvicorn

# ===== DB =====
db-start:
	brew services start postgresql@16

db-check:
	pg_isready -h localhost -p 5432

db-init:
	psql postgres -c "CREATE USER app WITH PASSWORD 'app';" || true
	psql postgres -c "CREATE DATABASE subs OWNER app;" || true

# ===== Backend =====
venv:
	test -d .venv || python3.11 -m venv .venv
	. .venv/bin/activate && pip install -r requirements.txt

migrate:
	. .venv/bin/activate && alembic upgrade head

seed:
	. .venv/bin/activate && python -m scripts.seed

run:
	. .venv/bin/activate && uvicorn app.main:app --reload --port 8000

# ===== 開発 =====
dev:
	make db-start
	make db-check
	make db-init
	make migrate
	make seed
	make run
