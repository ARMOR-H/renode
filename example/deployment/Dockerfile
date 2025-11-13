FROM debian:bookworm-slim
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y libicu-dev  && rm -rf /var/lib/apt/lists/*
ADD renode-1.16.0.linux-portable-dotnet.tar.gz /
RUN mv /renode_* /renode

WORKDIR /renode
ADD example example/

EXPOSE 12345
CMD ["./renode", "--console",  "example/p3.resc"]