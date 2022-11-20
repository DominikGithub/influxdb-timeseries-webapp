FROM python:3.11.0-slim-buster

ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip && pip install poetry

WORKDIR /code
COPY poetry.lock pyproject.toml /code/
RUN poetry config virtualenvs.create false && poetry install --no-root

COPY scraper_stocks.py /code/
CMD poetry run python scraper_stocks.py