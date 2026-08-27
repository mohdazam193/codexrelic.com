# Build stage
FROM alpine:3.20 AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apk update && apk upgrade && apk add --no-cache \
    python3 py3-pip \
    gcc musl-dev libffi-dev build-base \
    py3-cryptography py3-bcrypt

WORKDIR /build
COPY src/requirements.txt .

# Create a virtual environment and install dependencies
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir -r requirements.txt

# Final stage
FROM alpine:3.20

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_HOME=/app \
    PATH="/opt/venv/bin:$PATH"

# Install only runtime dependencies and create non-root user
RUN apk update && apk upgrade && apk add --no-cache \
    python3 py3-cryptography py3-bcrypt && \
    addgroup -S appgroup && adduser -S appuser -G appgroup

WORKDIR $APP_HOME

# Copy the virtual environment from the builder stage
COPY --from=builder /opt/venv /opt/venv

# Copy the application code
COPY src/ .

# Change ownership to the non-root user
RUN chown -R appuser:appgroup $APP_HOME

# Switch to the non-root user
USER appuser

EXPOSE 8000

CMD ["python3", "-m", "uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
