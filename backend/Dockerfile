# Use the official Python base image with Python 3.10
FROM python:3.10

# Set the working directory inside the container
WORKDIR /backend

# Copy the requirements file to the working directory
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code to the working directory
COPY . .

# Set the command to run the application
CMD ["python", "run.py"]