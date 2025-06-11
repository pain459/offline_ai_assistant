FROM python:3.10-slim

WORKDIR /app

# root start location to allow absolute imports.
ENV PYTHONPATH=/app

# Copy only requirements first to leverage Docker cache
# COPY requirements.txt .
# Copying .lock file generated from my production environment. This step is to ensure reproducability in case of debugging.
COPY requirements.lock .

# Install dependencies (cached unless requirements.txt changes)
# RUN pip install --no-cache-dir -r requirements.txt
# Adjusted the file to maintain uniformity. 
RUN pip install --no-cache-dir -r requirements.lock

# copy app code, templates, and static assets
COPY app/ ./app/
COPY templates/ ./templates/

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
