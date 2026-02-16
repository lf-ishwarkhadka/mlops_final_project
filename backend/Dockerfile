FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y curl build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and backend files
COPY requirements.txt .
COPY . ./backend

# Install dependencies
RUN pip install --default-timeout=1000 -r requirements.txt && \
    pip install --default-timeout=1000 torch --index-url https://download.pytorch.org/whl/cpu

# Create upload directory
RUN mkdir -p data/uploads

EXPOSE 8000

CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000"]
