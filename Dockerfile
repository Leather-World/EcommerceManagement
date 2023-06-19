# Use the official python base image
FROM python:3.9-slim-buster
# Set the working directory in the container
WORKDIR /app
# Copy the requirements file to the container
COPY requirements.txt .
# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
# Copy the application code to the container
COPY . .
# set the environment variable for Flask
ENV FLASK_APP=app.py
# Expose the port that Flask is running on
EXPOSE 5000
# Run the Flask application
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]