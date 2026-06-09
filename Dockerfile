FROM python:3.10-slim

WORKDIR /code

COPY ./pip-packages.txt /code/pip-packages.txt

RUN pip install --no-cache-dir --upgrade -r /code/pip-packages.txt

COPY ./src /code/src
COPY ./daycent /daycent

CMD ["python", "-m", "src.main"]
