# Use an official Python runtime as a parent image
FROM python:3.8-slim-buster

# Set the working directory in the container to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
ADD . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install FFmpeg
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y ffmpeg

# Make port 80 available to the world outside this container
EXPOSE 80

# Run bot.py when the container launches
CMD ["python", "bot.py"]