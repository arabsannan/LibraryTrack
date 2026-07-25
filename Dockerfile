# Use an official Python runtime
FROM python:3.12-slim

# Prevent Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE=1

# Ensure Python output is sent straight to the terminal
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies (optional but commonly needed)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency file first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project
COPY . /app/

# Collect static files (optional if using WhiteNoise)
RUN python manage.py collectstatic --noinput

# Expose the application port
ENV PORT=8000

# Start the Django application with Gunicorn
CMD gunicorn librarytrack.wsgi:application --bind 0.0.0.0:$PORT