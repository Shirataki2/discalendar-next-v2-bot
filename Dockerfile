# Build stage
FROM python:3.12-slim AS builder

WORKDIR /app

# Install uv
RUN pip install --no-cache-dir uv

# Copy dependency files
COPY pyproject.toml uv.lock* ./

# Install dependencies
RUN uv pip install --system --no-cache -r pyproject.toml

# Runtime stage
FROM python:3.12-slim

WORKDIR /app

# Create non-root user
RUN useradd --create-home --shell /bin/bash app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY src/ ./src/

# Change ownership
RUN chown -R app:app /app

USER app

# Run the bot
CMD ["python", "-m", "src.main"]
