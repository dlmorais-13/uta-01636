FROM python:3.10-slim

WORKDIR /code

COPY ./pip-packages.txt /code/pip-packages.txt

RUN pip install --no-cache-dir --upgrade -r /code/pip-packages.txt

COPY ./src /code/src

CMD ["python", "-m", "src.main"]

LABEL org.opencontainers.image.source="https://github.com/dlmorais-13/uta-01636.git"
