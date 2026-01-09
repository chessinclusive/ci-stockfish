FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080 \
    STOCKFISH_THREADS=2 \
    STOCKFISH_DEPTH=15

WORKDIR /app

# Install system deps and Stockfish engine
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc python3-dev stockfish \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app /app

EXPOSE ${PORT}

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]