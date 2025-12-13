# Use a small official Python image
FROM python:3.11-slim

WORKDIR /app

# Copy only requirements first for better caching
COPY requirements.txt .

# Use python -m pip and avoid cache
RUN python -m pip install --upgrade pip \
    && python -m pip install --no-cache-dir -r requirements.txt

# Copy application code (ensure filename matches your file: app1.py)
COPY app1.py .

# Create a non-root user and switch to it
RUN useradd --create-home --shell /bin/bash appuser \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 5000

# Use the lightweight Flask server for demo. For production use gunicorn.
CMD ["python", "app1.py"]