# Base image with Python
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy dependency files
COPY requirements.txt ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY . .

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000

# Expose Flask port
EXPOSE 5000

# Start the app
CMD ["flask", "run"]
