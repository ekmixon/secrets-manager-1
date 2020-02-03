FROM python:3.7.4-alpine3.10

RUN apk update
RUN apk add --no-cache build-base libffi-dev openssl-dev curl

RUN pip install --upgrade pip
RUN pip install pipenv

COPY ./Pipfile .
COPY ./Pipfile.lock .

RUN pipenv sync
COPY ./app/ ./app/
COPY ./docker_start.sh .
COPY ./run.py .

ENTRYPOINT [ "./docker_start.sh" ]