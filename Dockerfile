# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install the necessary Python packages
RUN pip install --no-cache-dir psycopg2-binary pika

# Make the Python script executable
RUN chmod +x main.py

# Produce output in container log
ENV PYTHONUNBUFFERED=1

# Define the command to run the script
CMD ["python", "-u", "./main.py"]

