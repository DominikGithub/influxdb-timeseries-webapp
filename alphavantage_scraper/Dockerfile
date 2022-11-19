FROM python:3.11.0-alpine3.16

ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip && pip install poetry

WORKDIR /code
COPY poetry.lock pyproject.toml /code/
COPY scraper_stocks.py /code/

RUN poetry config virtualenvs.create false && poetry install --no-root

CMD poetry run python scraper_stocks.py