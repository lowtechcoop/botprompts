FROM python:3.10

WORKDIR /code

ENV DOTENV=.env
ENV PYTHONPATH=/code

COPY ./backend/requirements.txt ./requirements.txt

RUN pip install --no-cache-dir --upgrade -r ./requirements.txt

COPY ./backend/alembic.ini ./alembic.ini
COPY ./backend/logging.json ./logging.json

COPY ./secrets/.backend.env ./.env

COPY ./backend/alembic ./alembic

COPY ./backend/app ./app

CMD [ "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--no-server-header" ]
