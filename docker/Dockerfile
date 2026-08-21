# Use official lightweight Python Alpine 3.20 image for minimal vulnerabilities
FROM python:3.11-alpine3.20

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_HOME=/app

# Set the working directory
WORKDIR $APP_HOME

# Install system dependencies (including precompiled cryptography/bcrypt to avoid slow rust compilation) and LaTeX
RUN apk update && apk upgrade && apk add --no-cache \
    gcc musl-dev libffi-dev build-base \
    py3-cryptography py3-bcrypt \
    texlive-xetex

# Install python dependencies (leverage Docker cache)
COPY src/requirements.txt .
RUN pip install --no-cache-dir --break-system-packages -r requirements.txt

# Copy the rest of the application code
COPY src/ .

# Expose the port the app runs on
EXPOSE 8000

# Run the FastAPI application using Uvicorn
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
