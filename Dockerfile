# Use the official Python image from Docker Hub
FROM python:3.8

# Set working directory within the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt /app/

# Install any dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Python script into the container
COPY . /app/

# Command to run on container start
CMD [ "python", "./crypto_monitor.py" ]
