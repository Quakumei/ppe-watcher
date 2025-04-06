FROM python:3.10-buster
RUN pip install poetry==2.0.1

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

COPY pyproject.toml poetry.lock README.md ./

RUN poetry install --without dev --no-root --no-interaction --no-ansi && rm -rf $POETRY_CACHE_DIR
RUN pip install 'git+https://github.com/facebookresearch/detectron2.git'

COPY . /app/


CMD [ "poetry", "run", "python3", "-m", "detection_system.main" ]