# Dockerfile
FROM python:3.10-slim

# Set environment variables
ENV PYTHONUNBUFFERED 1

# Create app directory
WORKDIR /app

# Copy requirements.txt and install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . /app/

# Expose the port for the bot (not strictly necessary for Telegram bot, but for good measure)
EXPOSE 8443

# Run the Python app
CMD ["python", "app.py"]
