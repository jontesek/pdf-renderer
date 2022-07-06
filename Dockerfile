FROM python:3.9-slim-bullseye

RUN \
    apt-get update &&\
    apt-get install -y --no-install-recommends tini && \
    pip install -U pip &&\
    pip install poetry==1.2.0b2 &&\
    poetry config virtualenvs.create false

WORKDIR /app
COPY poetry.lock pyproject.toml ./
RUN poetry install

COPY . .

EXPOSE 5000

USER nobody

ENTRYPOINT ["tini", "--"]