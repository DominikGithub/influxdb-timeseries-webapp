FROM python:3.11.0-slim-buster

ENV PYTHONUNBUFFERED 1
EXPOSE 8080

RUN pip install --upgrade pip && pip install poetry

WORKDIR /code
COPY poetry.lock pyproject.toml /code/
RUN poetry config virtualenvs.create false && poetry install --no-root

COPY dash_server.py /code/
CMD poetry run python dash_server.py