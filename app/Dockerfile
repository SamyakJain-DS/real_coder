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
    curl \
    ca-certificates \
    build-essential \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Python test runner used to drive the blink_tree test suite.
RUN pip install --no-cache-dir pytest==7.4.4

# Rust toolchain (stable, pinned to the crate's minimum supported
# version) installed via rustup. The cargo binary is placed on PATH
# so the test suite can build and run the blink_tree crate's tests.
ENV RUSTUP_HOME=/usr/local/rustup \
    CARGO_HOME=/usr/local/cargo \
    PATH=/usr/local/cargo/bin:$PATH
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs \
      | sh -s -- -y --no-modify-path --profile minimal --default-toolchain stable \
    && chmod -R a+w "$RUSTUP_HOME" "$CARGO_HOME"

# Pre-populate the cargo registry with the source crates the test
# suite will need at runtime. No compilation occurs here; this is
# a dependency download into $CARGO_HOME/registry, no different in
# kind from `pip install` or `apt-get install`.
RUN mkdir -p /tmp/fetch/src && cd /tmp/fetch \
    && printf '%s\n' \
        '[package]' \
        'name = "fetch_only"' \
        'version = "0.0.1"' \
        'edition = "2021"' \
        '' \
        '[dependencies]' \
        'arc-swap = "1"' \
        'crossbeam-epoch = "0.9"' \
        '' \
        '[dev-dependencies]' \
        'criterion = "0.5"' \
        > Cargo.toml \
    && touch src/lib.rs \
    && cargo fetch \
    && cd / && rm -rf /tmp/fetch

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
