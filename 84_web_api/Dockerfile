# Dockerfile for web_api
FROM python:3.9-alpine

# Set the working directory
WORKDIR /app

# Copy requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port the API will run on
EXPOSE 8080

# Run the web API
CMD ["python", "main.py"]
