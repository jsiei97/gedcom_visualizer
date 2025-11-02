FROM python:3.12-slim

# Install LaTeX and other required system packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    texlive-latex-base \
    texlive-latex-extra \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

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
