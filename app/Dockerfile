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
      | sh -s -- -y --no-modify-path --profile minimal --default-toolchain 1.75.0 \
    && chmod -R a+w "$RUSTUP_HOME" "$CARGO_HOME"

###############################################
# CARGO DEP CACHE (pre-compiled)
#
# Pre-build the exact dependency chain the evaluated crate uses
# (arc-swap + criterion + all transitive deps) into a shared target
# directory. Both the test runner crate and the user's crate point
# CARGO_TARGET_DIR at this location, so the heavy criterion build
# (~30 transitive crates) is compiled once at image-build time
# rather than on every evaluation.
#
# Version pins below mirror the precise pins recorded in the
# evaluated crate's Cargo.lock so the resolved package set matches
# and cargo reuses the cached .rlib outputs.
###############################################
ENV CARGO_TARGET_DIR=/usr/local/cargo-target

RUN mkdir -p /tmp/warmup/src /tmp/warmup/benches \
    && cd /tmp/warmup \
    && printf '%s\n' \
        '[package]' \
        'name = "warmup"' \
        'version = "0.0.1"' \
        'edition = "2021"' \
        '' \
        '[dependencies]' \
        'arc-swap = "1.7"' \
        '' \
        '[dev-dependencies]' \
        'criterion = "0.5"' \
        '' \
        '[[bench]]' \
        'name = "noop"' \
        'harness = false' \
        > Cargo.toml \
    && echo 'fn main() {}' > benches/noop.rs \
    && : > src/lib.rs \
    && cargo generate-lockfile \
    && cargo update -p clap        --precise 4.4.18 \
    && cargo update -p half        --precise 2.4.1  \
    && cargo update -p rayon       --precise 1.10.0 \
    && cargo update -p rayon-core  --precise 1.12.1 \
    && cargo bench --no-run \
    && cargo test  --no-run \
    && cd / \
    && rm -rf /tmp/warmup \
    && chmod -R a+w /usr/local/cargo-target /usr/local/cargo

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
