FROM python:3.7-slim
MAINTAINER zerthmonk

ENV PYTHONUBUFFERED=1
ENV PATH="/venv/bin:$PATH"

RUN apt-get update && \
    apt-get install -y --no-install-recommends curl

COPY ./requirements.txt /requirements.txt

ENV VENV="/venv"
RUN python -m venv $VENV
ENV PATH="$VENV/bin:$PATH"

RUN python -m pip install --upgrade pip && \
    python -m pip install -r /requirements.txt
