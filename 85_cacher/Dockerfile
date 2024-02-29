# Dockerfile for web_api
FROM python:3.9-alpine

# Set the working directory
WORKDIR /app

# Dockerfile for web_api
FROM python:3.9

# Set the working directory
WORKDIR /app

# Copy requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Set environment variable for cache file path
ENV CACHE_FILE_PATH /app/shared-cache

# Run the web API
CMD ["python", "main.py"]



# Copy requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Run the web API
CMD ["python", "main.py"]
