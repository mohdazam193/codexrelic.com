# Use official lightweight Python slim image for faster builds (prebuilt wheels)
FROM python:3.11-slim-bookworm

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_HOME=/app

# Set the working directory
WORKDIR $APP_HOME

# Install build dependencies for packages with C extensions and LaTeX compilation
RUN apk add --no-cache gcc musl-dev libffi-dev build-base texlive-xetex

# Install python dependencies (leverage Docker cache)
COPY src/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY src/ .

# Expose the port the app runs on
EXPOSE 8000

# Run the FastAPI application using Uvicorn
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
