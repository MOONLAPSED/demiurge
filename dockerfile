# Use Ubuntu as the base image
FROM ubuntu:22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies
RUN apt-get update && \
    apt-get install -y \
    git curl wget python3 python3-pip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Clone the latest release from GitHub
WORKDIR /app
RUN git clone --depth 1 --branch $(curl -s https://api.github.com/repos/open-webui/open-webui/releases/latest | grep -oP '"tag_name": "\K(.*)(?=")') https://github.com/open-webui/open-webui.git .

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Expose the default port (change if necessary)
EXPOSE 5000

# Run the application (modify the command if it has a specific entry point)
CMD ["python3", "webui.py"]
