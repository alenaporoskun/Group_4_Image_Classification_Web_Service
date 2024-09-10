# Stage 1: Build
FROM python:3.11-slim AS builder

# Install required system dependencies
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install dependencies for building
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev cmake zlib1g-dev libjpeg-dev libtiff-dev \
    libfreetype6-dev liblcms2-dev libwebp-dev libharfbuzz-dev libfribidi-dev \
    && rm -rf /var/lib/apt/lists/*

# Install work directory
WORKDIR /app

# Copy the poetry config file
COPY pyproject.toml poetry.lock /app/

# Install and upgrade pip, install poetry
RUN pip install --upgrade pip --no-cache-dir && pip install poetry

# Customize poetry configuration
RUN poetry config virtualenvs.create false && poetry install --no-dev --no-interaction --no-ansi

# Copy the rest of the code
COPY . /app/

# Collect static files
RUN python manage.py collectstatic --noinput

# Stage 2: Final
FROM python:3.11-slim

# Install required system dependencies
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV TF_ENABLE_ONEDNN_OPTS=1

# Install dependencies for running
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev zlib1g libjpeg62-turbo-dev libtiff6 libfreetype6 \
    liblcms2-2 libwebp7 libharfbuzz0b libfribidi0 \
    && rm -rf /var/lib/apt/lists/*

# Install work directory
WORKDIR /app

# Copy the installed dependencies from the build stage
COPY --from=builder /usr/local /usr/local

# Copy the rest of the code
COPY . /app/

# Open port 8000 for the application
EXPOSE 8000

# The command to run the application with optimized parameters Gunicorn
CMD ["gunicorn", "--worker-class", "gevent", "--workers", "1", "--timeout", "300", "image_web_classifier.wsgi:application", "--bind", "0.0.0.0:8000"]




