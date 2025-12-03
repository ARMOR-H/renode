FROM debian:bookworm-slim
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
        libicu-dev  \
        python3 \
        python3-pip \
        python3-paho-mqtt \
    && rm -rf /var/lib/apt/lists/*
ADD renode-1.16.0.linux-portable-dotnet.tar.gz /
RUN mv /renode_* /renode

WORKDIR /renode
ADD BLE_Beacon.elf ble_example/
ADD ble_example.repl ble_example/
ADD ble_example.resc ble_example/
ADD mqtt_connector.py ble_example/
ADD run.sh ble_example/

ENV MQTT_BROKER_HOST=8981c05c69e4403f80d287fcc63618fa.s1.eu.hivemq.cloud
ENV MQTT_BROKER_PORT=8883
ENV MQTT_TLS=1
ENV MQTT_USERNAME=username
ENV MQTT_PASSWORD=Upgrade25
ENV MQTT_TOPIC=carpetj1/photo 

EXPOSE 9999
CMD ["./ble_example/run.sh"]
