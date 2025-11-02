#!/bin/bash
# Script to set up and run GEDCOM Visualizer with DistroBox

set -e

# Configuration
IMAGE_NAME="gedcom-visualizer:latest"
CONTAINER_NAME="gedcom-viz"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}GEDCOM Visualizer DistroBox Setup${NC}"
echo -e "${GREEN}========================================${NC}"
echo

# Check if distrobox is installed
if ! command -v distrobox &> /dev/null; then
    echo -e "${RED}Error: distrobox is not installed.${NC}"
    echo "Please install distrobox first:"
    echo "  Visit: https://github.com/89luca89/distrobox"
    exit 1
fi

# Check if the container already exists
if distrobox list | grep -q "${CONTAINER_NAME}"; then
    echo -e "${YELLOW}Container '${CONTAINER_NAME}' already exists.${NC}"
    echo "Do you want to remove and recreate it? (y/N)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Removing existing container...${NC}"
        distrobox rm -f "${CONTAINER_NAME}"
    else
        echo -e "${GREEN}Entering existing container...${NC}"
        distrobox enter "${CONTAINER_NAME}"
        exit 0
    fi
fi

# Check if the image exists
if ! podman images | grep -q "gedcom-visualizer"; then
    echo -e "${YELLOW}Container image not found. Building it first...${NC}"
    ./build-container.sh
fi

echo -e "${GREEN}Creating DistroBox container '${CONTAINER_NAME}'...${NC}"
distrobox create --image "${IMAGE_NAME}" --name "${CONTAINER_NAME}"

echo
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Setup complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo
echo "To enter the container, run:"
echo "  distrobox enter ${CONTAINER_NAME}"
echo
echo "Inside the container, you can use:"
echo "  gedcom-list /path/to/file.ged"
echo "  gedcom-generate /path/to/file.ged @I1@ -o output.adoc"
echo "  gedcom-convert output.adoc -o output.pdf"
echo
echo "Your home directory is automatically mounted in the container."
echo
