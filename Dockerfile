FROM python:3.7-slim
MAINTAINER zerthmonk

ENV PYTHONUBUFFERED=1
ENV PATH="/venv/bin:$PATH"

COPY ./requirements.txt /requirements.txt

ENV VENV="/venv"
RUN python -m venv $VENV
ENV PATH="$VENV/bin:$PATH"

RUN python -m pip install --upgrade pip && \
    python -m pip install -r /requirements.txt

COPY ./skabenproto /skabenproto
COPY ./deploy.sh /deploy.sh

ENTRYPOINT flake8 /skabenproto; pytest /skabenproto
