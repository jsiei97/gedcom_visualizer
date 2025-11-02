# Multi-stage Dockerfile for GEDCOM Visualizer

# Base stage with common dependencies
FROM python:3.12-slim as base

# Install LaTeX and other required system packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    texlive-latex-base \
    texlive-latex-extra \
    texlive-fonts-recommended \
    texlive-latex-recommended \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Development stage - for VS Code devcontainer
FROM base as development

# Install additional development tools and VS Code requirements
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    vim \
    nano \
    curl \
    wget \
    build-essential \
    sudo \
    xxd \
    && rm -rf /var/lib/apt/lists/*

# Install additional Python development tools
RUN pip install --no-cache-dir \
    pylint \
    black \
    flake8 \
    pytest \
    ipython \
    jupyter \
    debugpy

# Create a non-root user with sudo access for development
RUN useradd -m -u 1000 -s /bin/bash devuser && \
    echo "devuser ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers && \
    chown -R devuser:devuser /workspace

# Set up the Python path for development
ENV PYTHONPATH="/workspace:$PYTHONPATH"
ENV IN_CONTAINER=true

USER root
# Copy the entire project (this will be overridden by volume mount in devcontainer)
COPY . .
RUN pip install -e . && chown -R devuser:devuser /workspace
USER devuser

# Default command
CMD ["/bin/bash"]

# Production stage - for DistroBox and production use  
FROM base as production

# Copy the entire project
COPY . .

# Install the package in development mode
RUN pip install -e .

# Create a non-root user for DistroBox compatibility
RUN useradd -m -u 1000 -s /bin/bash user && \
    chown -R user:user /workspace

USER user

# Set environment variable to indicate we're in a container
ENV IN_CONTAINER=true

# Default command - open a bash shell
CMD ["/bin/bash"]
