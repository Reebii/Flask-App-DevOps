# Use the official Python image from Docker Hub
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy all files to container
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port your app runs on
EXPOSE 5000

# Run the app
CMD ["python", "app.py"]
