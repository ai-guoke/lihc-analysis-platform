# Multi-stage Docker build for LIHC Platform
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PYTHONPATH=/app

# Create non-root user
RUN groupadd -r lihc && useradd -r -g lihc lihc

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt requirements-api.txt ./

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install -r requirements-api.txt

# Development stage
FROM base as development

# Install development dependencies
RUN pip install pytest pytest-cov black isort flake8 mypy pre-commit

# Copy source code
COPY . .

# Create necessary directories
RUN mkdir -p logs uploads results temp cache data config \
    data/raw data/processed data/external \
    results/tables results/networks results/linchpins results/figures \
    results/user_analyses notebooks

# Make scripts executable
RUN chmod +x demo.py run_pipeline.py demo_phase2.py demo_phase3.py

# Change ownership to lihc user
RUN chown -R lihc:lihc /app

# Switch to non-root user
USER lihc

# Expose ports (API and Dashboard)
EXPOSE 8050 8051

# Development command
CMD ["python", "-m", "uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8050", "--reload"]

# Production stage
FROM base as production

# Copy only necessary files
COPY src/ ./src/
COPY main.py ./
COPY run_pipeline.py ./
COPY pyproject.toml ./
COPY Makefile ./

# Create necessary directories
RUN mkdir -p logs uploads results temp cache data config \
    data/raw data/processed data/external \
    results/tables results/networks results/linchpins results/figures \
    results/user_analyses

# Create optimized Python cache
RUN python -m compileall src/

# Change ownership to lihc user
RUN chown -R lihc:lihc /app

# Switch to non-root user
USER lihc

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8050/health || exit 1

# Expose port
EXPOSE 8050

# Production command
CMD ["python", "-m", "uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8050", "--workers", "4"]