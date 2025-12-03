#!/bin/bash

/renode/renode --disable-gui /renode/ble_example/ble_example.resc &
python3 /renode/ble_example/mqtt_connector.py 
