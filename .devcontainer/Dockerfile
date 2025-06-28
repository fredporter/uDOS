FROM debian:bullseye

# Install basic tools
RUN apt-get update && apt-get install -y \
    bash curl git vim nano tree \
    docker.io unzip less net-tools \
    && apt-get clean

# Optional: timezone, locales, etc.
ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /uDOS