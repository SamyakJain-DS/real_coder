###############################################
# BASE IMAGE
###############################################
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

###############################################
# SYSTEM DEPENDENCIES
###############################################
RUN apt-get update && apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    git \
    python3 \
    python3-pip \
    python3-setuptools \
    python-is-python3 \
    unzip \
    && mkdir -p /etc/apt/keyrings \
    && curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg \
    && echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_20.x nodistro main" > /etc/apt/sources.list.d/nodesource.list \
    && apt-get update \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

###############################################
# NODE DEPENDENCIES
###############################################
RUN mkdir -p /deps \
    && cd /deps \
    && npm init -y \
    && npm_config_registry=http://registry.npmjs.org/ npm install --no-audit --no-fund \
        @types/node@^20.12.7 \
        typescript@^5.4.5 \
        vitest@^2.1.9 \
        marked@^12.0.0 \
        highlight.js@^11.10.0 \
        pdf-lib@^1.17.1 \
    && npm cache clean --force

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
