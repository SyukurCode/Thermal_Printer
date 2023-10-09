# syntax=docker/dockerfile:1

FROM python:3.9-slim-buster
#FROM arm32v7/python:3
#FROM arm64v8/python:3

WORKDIR /app

RUN python -m pip install --upgrade pip

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

CMD [ "python3", "index.py"]

