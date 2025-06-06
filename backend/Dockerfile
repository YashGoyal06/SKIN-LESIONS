# Use an official Python image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all files into the container
COPY . .

# Expose the port Flask will run on
EXPOSE 7860

# Run your Flask app
CMD ["python", "app.py"]
