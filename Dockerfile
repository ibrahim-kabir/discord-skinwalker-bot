# Use an official Python runtime as a parent image
FROM python:3.8-slim-buster

# Set the working directory in the container to /app
WORKDIR /app

# Install FFmpeg
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y ffmpeg

# Make port 80 available to the world outside this container
EXPOSE 80

# Install any needed packages specified in requirements.txt
CMD pip install --no-cache-dir -r requirements.txt && python app/main.py
