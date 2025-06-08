FROM python:3.10-slim

WORKDIR /app

# Copy only requirements first to leverage Docker cache
COPY requirements.txt .

# Install dependencies (cached unless requirements.txt changes)
RUN pip install --no-cache-dir -r requirements.txt

# copy app code, templates, and static assets
COPY app/ ./app/
COPY templates/ ./templates/

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
