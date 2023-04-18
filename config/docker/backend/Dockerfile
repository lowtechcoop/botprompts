FROM python:3.10

WORKDIR /code

ENV DOTENV=.env
ENV PYTHONPATH=/code

COPY ./backend/requirements.txt ./requirements.txt

RUN pip install --no-cache-dir --upgrade -r ./requirements.txt

COPY ./config/docker/backend/launch.sh ./launch.sh

RUN chmod +x ./launch.sh

COPY ./backend/alembic.ini ./alembic.ini
COPY ./backend/logging.json ./logging.json

COPY ./secrets/.backend.env ./.env

COPY ./backend/alembic ./alembic

COPY ./backend/app ./app

CMD [ "./launch.sh" ]
