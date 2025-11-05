FROM ubuntu:22.04
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    wget \
    apt-transport-https \
    dirmngr \
    gnupg \
    ca-certificates \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

RUN add-apt-repository ppa:dotnet/backports -y \
    && apt-get update && apt-get install -y \
    dotnet-sdk-9.0  \
    dotnet-runtime-9.0 \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y \
    git \
    automake \
    cmake \
    autoconf \
    libtool \
    g++ \
    coreutils \
    policykit-1 \
    libgtk-3-dev \
    uml-utilities \
    gtk-sharp3 \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

ADD ./ /tmp/renode
RUN pip3 install --no-cache-dir -r /tmp/renode/tests/requirements.txt