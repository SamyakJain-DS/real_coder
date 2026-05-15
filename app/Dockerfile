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
# NODE.JS 18 LTS
###############################################
RUN apt-get update && apt-get install -y curl \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

###############################################
# JAVASCRIPT / TYPESCRIPT TEST DEPENDENCIES
###############################################
RUN echo '{"name":"knife-collection-tests","version":"1.0.0","private":true}' > package.json && \
    npm install --save-dev \
        vitest@1.6.0 \
        @vitejs/plugin-react@4.3.1 \
        @testing-library/react@14.3.1 \
        @testing-library/user-event@14.5.2 \
        @testing-library/jest-dom@6.4.6 \
        jsdom@24.1.3 \
        react@18.3.1 \
        react-dom@18.3.1 \
        typescript@5.4.5 \
        @types/react@18.3.3 \
        @types/react-dom@18.3.0 \
        vite@5.2.0

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
