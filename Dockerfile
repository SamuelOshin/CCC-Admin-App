# Use a Python Debian-slim image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/scripts:${PATH}"

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ pkg-config libmariadb-dev git curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create a non-root user
ARG UID=1000
ARG GID=1000
RUN groupadd -g ${GID} appuser && \
    useradd -u ${UID} -g appuser -m appuser

# Create directories
RUN mkdir -p /app /scripts /vol/web/media /vol/web/static && \
    chown -R appuser:appuser /app /scripts /vol

# Switch to non-root user
USER appuser

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY --chown=appuser:appuser ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY --chown=appuser:appuser . /app/

# Copy scripts
COPY --chown=appuser:appuser ./scriptts /scripts/
RUN chmod +x /scripts/*

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# Specify the command to run when the container starts
CMD ["entrypoint.sh"]
