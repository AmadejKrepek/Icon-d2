# Dockerfile for web_api
FROM python:3.9

# Install GDAL dependencies
RUN apt-get update && \
    apt-get install -y libgdal-dev

# Set the working directory
WORKDIR /app

# Copy requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN pip install --no-cache-dir --force-reinstall 'GDAL[numpy]==3.6.2'

# Copy the rest of the application code
COPY . .

# Run the web API
CMD ["python", "main.py"]
