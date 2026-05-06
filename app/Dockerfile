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
# PRE-WARM NUGET PACKAGE CACHE
# Creates a temporary project with the same dependencies the solution
# uses, runs dotnet restore during image build (host has full internet
# access), then removes the temp project. The global packages cache at
# /root/.nuget/packages persists in the image so the container never
# needs to reach api.nuget.org at runtime.
###############################################
RUN mkdir -p /tmp/nuget-warmup && \
    printf '<Project Sdk="Microsoft.NET.Sdk.Web">\n\
  <PropertyGroup>\n\
    <TargetFramework>net8.0</TargetFramework>\n\
  </PropertyGroup>\n\
  <ItemGroup>\n\
    <PackageReference Include="Microsoft.EntityFrameworkCore.Sqlite" Version="8.0.0" />\n\
    <PackageReference Include="Microsoft.EntityFrameworkCore.Design" Version="8.0.0" />\n\
  </ItemGroup>\n\
</Project>\n' > /tmp/nuget-warmup/warmup.csproj && \
    dotnet restore /tmp/nuget-warmup/warmup.csproj && \
    rm -rf /tmp/nuget-warmup
 
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
