FROM debian:bullseye

# Install basic tools and Python
RUN apt-get update && apt-get install -y \
    bash curl git vim nano tree \
    docker.io unzip less net-tools \
    python3 python3-pip \
    && apt-get clean

# Optional: timezone, locales, etc.
ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /uDOS

# Install Python requirements if requirements.txt exists
COPY ../requirements.txt /uDOS/requirements.txt
RUN pip3 install --no-cache-dir