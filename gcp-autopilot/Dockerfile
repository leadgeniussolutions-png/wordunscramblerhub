FROM python:3.11-slim

# Install git, curl, and wordlists for dictionary generation
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    wamerican \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT=8080
ENV PYTHONUNBUFFERED=1

CMD ["gunicorn", "-b", "0.0.0.0:8080", "--workers", "2", "--timeout", "300", "main:app"]
