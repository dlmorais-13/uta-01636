FROM python:3.10-slim

RUN pip install poetry

WORKDIR /code

COPY ./pyproject.toml /code/
COPY ./poetry.lock /code/

RUN poetry install

COPY ./src /code/src
COPY ./daycent /daycent

CMD ["python", "-m", "src.main"]
