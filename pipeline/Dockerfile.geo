# ============================================
# GenHack Climate - Geospatial Dockerfile
# ============================================
# Multi-stage build for optimized image size

FROM python:3.11-slim AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages in builder
WORKDIR /install
COPY pipeline/requirements.txt /install/
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ============================================
# Final stage
# ============================================
FROM python:3.11-slim

# Install GDAL and geospatial libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    gdal-bin \
    libgdal-dev \
    proj-bin \
    proj-data \
    libproj-dev \
    libgeos-dev \
    geotiff-bin \
    # Weasyprint dependencies
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    libffi-dev \
    libcairo2 \
    libcairo2-dev \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

# Set GDAL environment variables
ENV GDAL_CONFIG=/usr/bin/gdal-config
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

# Copy installed Python packages from builder
COPY --from=builder /install /usr/local

# Setup application
WORKDIR /app

# Copy source code
COPY src/ /app/src/
COPY pipeline/ /app/pipeline/
COPY configs/ /app/configs/
COPY schemas/ /app/schemas/
COPY templates/ /app/templates/

# Create output directories
RUN mkdir -p /tmp/genhack/{raw,intermediate,features,models,exports,configs,logs}

# Set Python path
ENV PYTHONPATH=/app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Default entrypoint and command
ENTRYPOINT ["python", "pipeline/job_main.py"]
CMD ["--config", "configs/paris_2022_mock.yml"]
