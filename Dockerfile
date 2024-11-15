# Use a Python Debian-slim image
FROM python:3.11-slim

ENV PATH="/scripts:${PATH}"

# Copy the requirements file to the container
COPY ./requirements.txt /requirements.txt

# Install necessary build dependencies, including git and MySQL libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ pkg-config libmariadb-dev git && \
    pip install -r /requirements.txt && \
    apt-get remove -y gcc g++ && \
    apt-get autoremove -y && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create a directory for the app files
RUN mkdir /app

# Copy all files from the host to the app directory in the container
COPY . /app/

# Set the working directory to /app
WORKDIR /app

# Copy any scripts to the /scripts directory in the container
COPY ./scriptts /scripts

# Grant execute permissions to all files in the /scripts directory
RUN chmod +x /scripts/*

# Create directories for media and static files
RUN mkdir -p /vol/web/media /vol/web/static

# Create a non-root user named 'user' for security purposes
RUN useradd -m user && chown -R user:user /vol

# Set directory permissions to be accessible by all users
RUN chmod -R 755 /vol/web

# Switch to the non-root user for running the application
USER user

# Specify the command to run when the container starts
CMD ["entrypoint.sh"]
