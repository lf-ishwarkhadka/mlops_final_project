FROM python:3.11-slim

WORKDIR /app

# Copy requirements and frontend files
COPY requirements.txt .
COPY . ./frontend

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8501

CMD ["streamlit", "run", "frontend/app.py", "--server.address", "0.0.0.0"]
