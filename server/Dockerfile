# Use an official Python runtime as a parent image
FROM python:3.10-slim

RUN apt-get -y update && apt-get -y install curl

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY server.py /app/server.py



ARG ENV

# Set the environment variable
ENV ENV="prod"

# Run script.py when the container launches
CMD ["python", "server.py"]
