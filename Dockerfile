FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000 \
    STOCKFISH_THREADS=2 \
    STOCKFISH_DEPTH=15

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc python3-dev stockfish \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ✅ Copy everything (so app.py + STOCKFISH.py are included)
COPY . .

EXPOSE 8000

# ✅ app.py is at repo root, so "app:app" is correct
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
