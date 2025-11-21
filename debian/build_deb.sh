#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Define variables
DEB_BUILD_DIR="debian-builds"
OUTPUT_DIR="${DEB_BUILD_DIR}/output"
CONTAINERFILE_PATH="${DEB_BUILD_DIR}/Containerfile"
IMAGE_NAME="flix-cli-builder"
DEB_PACKAGE_NAME="flix-cli_1.8.0_all.deb" # Assuming this name based on previous output

echo "Starting .deb package build process..."

# 1. Create the debian-builds directory if it doesn't exist
echo "Creating directory: ${DEB_BUILD_DIR}"
mkdir -p "${DEB_BUILD_DIR}"

# 2. Create the output directory inside debian-builds
echo "Creating output directory: ${OUTPUT_DIR}"
mkdir -p "${OUTPUT_DIR}"

# 3. Write the Containerfile
echo "Writing Containerfile to ${CONTAINERFILE_PATH}"
cat <<EOF > "${CONTAINERFILE_PATH}"
# Use a Debian base image
FROM debian:stable-slim

# Install dependencies for fpm and python
RUN apt-get update && \
    apt-get install -y ruby ruby-dev build-essential git python3 python3-pip python3-venv && \
    rm -rf /var/lib/apt/lists/*

# Install fpm
RUN gem install fpm

# Create a virtual environment
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy the application source
COPY . /app
WORKDIR /app

# Install Python dependencies
RUN pip install .
RUN pip install packaging

# Build the .deb package using fpm
RUN fpm -s python -t deb \
    -n flix-cli \
    -v 1.8.0 \
    --description "A high efficient, powerful and fast movie scraper." \
    --python-package-name-prefix python3 \
    --python-bin /opt/venv/bin/python3 \
    --depends ffmpeg \
    --depends fzf \
    --depends mpv \
    ./
EOF

# 4. Build the Podman image
echo "Building Podman image: ${IMAGE_NAME}"
podman build -t "${IMAGE_NAME}" -f "${CONTAINERFILE_PATH}" .

# 5. Run the container to copy the .deb package to the host
echo "Copying .deb package to ${OUTPUT_DIR}"
podman run --rm -v "$(pwd)/${OUTPUT_DIR}:/packages" "${IMAGE_NAME}" sh -c "cp /app/${DEB_PACKAGE_NAME} /packages"

echo "Build process complete. The .deb package is available at: ${OUTPUT_DIR}/${DEB_PACKAGE_NAME}"
