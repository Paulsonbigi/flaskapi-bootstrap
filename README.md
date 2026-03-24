python3 -m venv env
source env/bin/activate
pip install fastapi sqlalchemy psycopg2-binary uvicorn

pip freeze > requirements.txt

pip install <package> && pip freeze > requirements.txt

# Create a new migration after changing a model
alembic revision --autogenerate -m "add users table"

# Apply all pending migrations to the DB
alembic upgrade head

# Roll back the last migration
alembic downgrade -1

# Roll back all migrations
alembic downgrade base

# See current migration status
alembic current

# See migration history
alembic history