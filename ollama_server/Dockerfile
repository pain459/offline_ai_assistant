FROM python:3.10-slim

# Copy only requirements first to leverage Docker cache
# COPY requirements.txt .
# Copying .lock file generated from my production environment. This step is to ensure reproducability in case of debugging.
COPY requirements.lock .

# Install dependencies (cached unless requirements.txt changes)
# RUN pip install --no-cache-dir -r requirements.txt
# Adjusted the file to maintain uniformity. 
RUN pip install --no-cache-dir -r requirements.lock

WORKDIR /app

# root start location to allow absolute imports.
ENV PYTHONPATH=/app

# Install CA certificates to allow TLS verification
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates && rm -rf /var/lib/apt/lists/*

# copy app code, templates, and static assets
COPY app/ ./app/
COPY templates/ ./templates/

# Default state: disable
# Enable the entire section if there is a need of custom certificates. Adjust certificate names accordingly.
#---------------- start
# Copy and trust the custom root certificate
# COPY ./app/huggingface.co.crt /usr/local/share/ca-certificates/
# RUN update-ca-certificates

# # Ensure Python uses the correct CA bundle
# ENV REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
# ENV SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt
#---------------- end

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
