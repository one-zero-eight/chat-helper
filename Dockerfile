FROM python:3.12-slim

WORKDIR /usr/src/app

COPY pyproject.toml poetry.lock ./

RUN pip install poetry && poetry config virtualenvs.create false && poetry install --no-root

COPY static static
COPY src src

CMD ["python", "-m", "src.bot"]
