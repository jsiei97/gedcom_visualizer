#!/bin/bash
# Script to build the GEDCOM Visualizer Docker container using Podman

set -e

# Configuration
IMAGE_NAME="gedcom-visualizer"
IMAGE_TAG="latest"
FULL_IMAGE_NAME="${IMAGE_NAME}:${IMAGE_TAG}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Building GEDCOM Visualizer Container${NC}"
echo -e "${GREEN}========================================${NC}"
echo

# Check if podman is installed
if ! command -v podman &> /dev/null; then
    echo -e "${RED}Error: podman is not installed.${NC}"
    echo "Please install podman first:"
    echo "  Ubuntu/Debian: sudo apt-get install podman"
    echo "  Fedora: sudo dnf install podman"
    echo "  Arch: sudo pacman -S podman"
    exit 1
fi

echo -e "${YELLOW}Building container image: ${FULL_IMAGE_NAME}${NC}"
echo

# Build the container using podman
podman build -t "${FULL_IMAGE_NAME}" .

if [ $? -eq 0 ]; then
    echo
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}Container built successfully!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo
    echo "Image name: ${FULL_IMAGE_NAME}"
    echo
    echo "To run the container with podman:"
    echo "  podman run -it --rm ${FULL_IMAGE_NAME}"
    echo
    echo "To use with DistroBox:"
    echo "  distrobox create --image ${FULL_IMAGE_NAME} --name gedcom-viz"
    echo "  distrobox enter gedcom-viz"
    echo
    echo "To mount your GEDCOM files:"
    echo "  podman run -it --rm -v /path/to/gedcom/files:/data ${FULL_IMAGE_NAME}"
    echo
else
    echo -e "${RED}Error: Container build failed.${NC}"
    exit 1
fi
