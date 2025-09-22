# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy project files
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir Flask Flask-SQLAlchemy

# Expose the port Flask uses
EXPOSE 5000

# Run the app
CMD ["python", "app.py"]
