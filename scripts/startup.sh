#!/bin/bash
echo "waiting for HA to become responsive..."
until $(curl --output /dev/null --silent --get --fail http://192.168.1.2:8123); do
    printf '.'
    sleep 5
done
echo "running chromium."
chromium --kiosk --enable-features=OverlayScrollbar --disk-cache-dir=/dev/null --disk-cache-size=1 http://192.168.1.2:8123/
