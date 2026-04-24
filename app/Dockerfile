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
# PYTHON DEPENDENCIES
# The donor_pipeline package depends on pandas, numpy and scikit-learn
# (pinned to the versions mandated by the prompt's requirements.txt).
# pytest is installed solely to execute the test suite; it is never
# imported by donor_pipeline.
###############################################
RUN pip3 install --no-cache-dir \
    pytest \
    pandas==2.2.2 \
    numpy==1.26.4 \
    scikit-learn==1.5.0

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
