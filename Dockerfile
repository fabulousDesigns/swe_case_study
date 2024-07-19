# Using a multi-stage build to optimize image size
FROM python:3.12-slim AS builder
WORKDIR /app

# Installing system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Installing Python dependencies
COPY requirements.txt .
RUN python -m pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install psycopg2-binary

# Copying application code
COPY . .

# Using a new stage to create the final image
FROM python:3.12-slim
WORKDIR /app

# Installing system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copying installed dependencies from the builder stage
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copying application code from the builder stage
COPY --from=builder /app .

# Exposing the port that uvicorn will use
EXPOSE 8001

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]

# Labels for the image
LABEL maintainer="Bernard Maina"
LABEL version="1.0"
LABEL description="Case Study"