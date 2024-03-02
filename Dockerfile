FROM python:3.11-slim

WORKDIR /usr/src/app

COPY pyproject.toml .

RUN pip install poetry && poetry config virtualenvs.create false && poetry install --no-root

COPY . .

CMD ["python", "./bot.py"]
