# --- Build Stage ---
# Use an official Python runtime as a parent image
FROM python:3.12-slim as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Install system dependencies needed for psycopg2 (PostgreSQL adapter)
RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev

# Install Python dependencies
# Copy only the requirements file to leverage Docker's layer caching
COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /app/wheels -r requirements.txt


# --- Final Stage ---
FROM python:3.12-slim

# Create a non-root user for security
RUN addgroup --system app && adduser --system --group app

# Set the working directory
WORKDIR /app

# Copy installed dependencies from the builder stage
COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache /wheels/*

# Copy the entire project directory into the container
COPY . .

# Change ownership to the new user
RUN chown -R app:app /app

# Switch to the non-root user
USER app

# The default command to run when the container starts
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]