FROM python:3.9
WORKDIR /code
RUN pip3 install poetry
COPY pyproject.toml poetry.lock /code
RUN poetry install
COPY . /code
CMD gunicorn foodgram.wsgi:application --bind 0.0.0.0:8000