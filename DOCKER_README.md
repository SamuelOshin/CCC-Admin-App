# CCC Administrative App - Docker Setup

This Django application is containerized following security best practices.

## Prerequisites

- Docker and Docker Compose installed
- Git (for cloning if needed)

## Setup

1. Clone the repository (if not already done):
   ```bash
   git clone <repository-url>
   cd ccc-admin-app
   ```

2. Create environment file:
   ```bash
   cp .env.example .env
   ```

3. Edit `.env` with your secure values:
   - Generate a strong SECRET_KEY
   - Set secure database passwords
   - Adjust UID/GID if needed (defaults to 1000)

4. Build and start the containers:
   ```bash
   docker-compose up --build
   ```

## Security Features

- **Non-root user**: Application runs as non-root user (appuser with UID 1000)
- **Minimal base image**: Uses python:3.11-slim
- **Environment variables**: Secrets managed via environment variables
- **No source mounting**: Source code not mounted in production
- **Health checks**: Container health monitored
- **Proper permissions**: Directories owned by application user
- **Dependency optimization**: Python packages installed without cache

## Services

- **web**: Django application with Gunicorn
- **db**: MySQL 8.0 database
- **nginx**: Reverse proxy and static file server

## Production Deployment

- Set DEBUG=False in .env
- Use strong, unique passwords
- Configure proper domain in nginx.conf
- Use Docker secrets or external secret management
- Enable SSL/TLS termination

## Health Checks

- Application health: http://localhost/health/
- Database health: Built-in MySQL health check

## Volumes

- mysql_data: Persistent database storage
- static_volume: Collected static files
- media_volume: User uploaded media files