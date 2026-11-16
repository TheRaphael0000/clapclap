FROM python:3.13-slim

WORKDIR /app

COPY pyproject.toml README.md ./
RUN pip install --only-deps ".[server]"
COPY src src
RUN pip install --no-deps ".[server]"

ENTRYPOINT ["clapclap"]