# Use an official Python runtime as a parent image
FROM python

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file first to leverage Docker cache
COPY req.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r req.txt

# Copy the application code into the container
COPY FISH_PROJECT ./FISH_PROJECT
COPY json ./json

# Run the application

CMD ["/bin/bash", "-c", "python FISH_PROJECT/Main.py"]