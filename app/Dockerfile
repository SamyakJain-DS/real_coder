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
    curl \
    ca-certificates \
    gnupg \
    python3 \
    python3-pip \
    python3-setuptools \
    python-is-python3 \
    unzip \
    zip \
    && rm -rf /var/lib/apt/lists/*

###############################################
# NODE.JS 20 LTS
# Tests run on Node via native ES modules; jsdom is the sole npm dependency.
###############################################
RUN mkdir -p /etc/apt/keyrings \
    && curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key \
        | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg \
    && echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_20.x nodistro main" \
        > /etc/apt/sources.list.d/nodesource.list \
    && apt-get update \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

###############################################
# PRE-INSTALL TEST DEPENDENCIES
# jsdom is the sole npm dependency used by the test suite.
# The install is wrapped in a retry loop because npm's streaming TLS
# occasionally fails with ERR_SSL_CIPHER_OPERATION_FAILED under WSL2.
###############################################
RUN mkdir -p /deps \
    && cd /deps \
    && echo '{"name":"test-deps","type":"module","dependencies":{"jsdom":"^24.0.0"}}' > package.json \
    && npm config set fetch-retries 5 \
    && npm config set fetch-retry-mintimeout 20000 \
    && npm config set fetch-retry-maxtimeout 120000 \
    && npm config set registry https://registry.npmjs.org/ \
    && ( npm install --no-audit --no-fund --prefer-online \
         || (sleep 5 && npm install --no-audit --no-fund --prefer-online) \
         || (sleep 10 && npm install --no-audit --no-fund --prefer-online) ) \
    && rm package.json

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