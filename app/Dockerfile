###############################################
# BASE IMAGE
###############################################
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

###############################################
# SYSTEM DEPENDENCIES
###############################################
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    python3-setuptools \
    python-is-python3 \
    unzip \
    && rm -rf /var/lib/apt/lists/*
 
###############################################
# .NET 8 SDK
###############################################
RUN apt-get update && apt-get install -y wget ca-certificates && \
    wget https://packages.microsoft.com/config/ubuntu/22.04/packages-microsoft-prod.deb \
         -O /tmp/packages-microsoft-prod.deb && \
    dpkg -i /tmp/packages-microsoft-prod.deb && \
    rm /tmp/packages-microsoft-prod.deb && \
    apt-get update && apt-get install -y dotnet-sdk-8.0 && \
    rm -rf /var/lib/apt/lists/*
 
###############################################
# PYTHON TEST DEPENDENCIES
###############################################
RUN pip3 install --no-cache-dir pytest requests

###############################################
# WORKING DIRECTORY + GIT SETUP
###############################################
WORKDIR /app

RUN git init \
    && git config --global user.email "agent@example.com" \
    && git config --global user.name "Agent" \
    && echo "# Workspace" > README.md \
    && git add README.md \
    && git commit -m "Initial commit"

###############################################
# EVALUATION ASSETS DIRECTORY
###############################################
# Populated at RUNTIME by the evaluation script.
RUN mkdir -p /eval_assets

CMD ["/bin/bash"]
