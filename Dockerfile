# Base image
FROM python:3.10-slim

# Prevent Python from writing .pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip --disable-pip-version-check \
    && pip install --no-cache-dir --disable-pip-version-check -r requirements.txt

# Copy application code
COPY . . 