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
    software-properties-common \
    unzip \
    && add-apt-repository -y ppa:deadsnakes/ppa \
    && apt-get update \
    && apt-get install -y \
    python3.11 \
    python3.11-venv \
    python3.11-distutils \
    && rm -rf /var/lib/apt/lists/*

RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1 \
    && update-alternatives --install /usr/bin/python python /usr/bin/python3.11 1

RUN python3.11 -m ensurepip --upgrade \
    && python3.11 -m pip install --no-cache-dir \
        "pytest>=7.0" \
        pandas \
        numpy \
        scikit-learn \
        matplotlib \
        seaborn

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