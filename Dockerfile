FROM python:3.7-slim
MAINTAINER zerthmonk

ENV PYTHONUBUFFERED=1
ENV PATH="/venv/bin:$PATH"

RUN apt-get update && \
    apt-get install -y --no-install-recommends curl

COPY ./build_requirements.txt /build_requirements.txt

RUN python -m pip install --upgrade pip && \
    python -m pip install -r /build_requirements.txt && \

COPY . /app

CMD ["sh", "-c", "chmod", "+x", "/app/entrypoint.sh"]
CMD ["sh", "-c", "/app/entrypoint.sh"]
