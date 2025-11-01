#!/bin/bash
# Setup script for Mosquitto MQTT broker
set -e

echo "========================================="
echo "Setting up Mosquitto MQTT Broker"
echo "========================================="
echo ""

MQTT_USER="${1:-mqtt}"
MQTT_PASSWORD="${2:-}"
WORK_DIR="$(pwd)"

# Create directories
echo "Creating directories..."
sudo mkdir -p mosquitto/config
sudo mkdir -p mosquitto/data
sudo mkdir -p mosquitto/log

# Copy config file
echo "Creating configuration..."
sudo cp mosquitto.conf mosquitto/config/mosquitto.conf

# Set permissions (mosquitto runs as UID 1883)
echo "Setting permissions..."
sudo chown -R 1883:1883 mosquitto
sudo chmod -R 755 mosquitto

if [ -z "$MQTT_PASSWORD" ]; then
    echo ""
    echo "Please enter password for MQTT user '$MQTT_USER':"
    read -s MQTT_PASSWORD
    echo ""
fi

# Create password file using docker
echo "Creating password file..."
docker run --rm -v "$(pwd)/mosquitto/config:/mosquitto/config" eclipse-mosquitto:2.0 \
    mosquitto_passwd -c -b /mosquitto/config/password.txt "$MQTT_USER" "$MQTT_PASSWORD"

# Fix permissions on password file
sudo chown 1883:1883 mosquitto/config/password.txt
sudo chmod 600 mosquitto/config/password.txt

echo ""
echo "✓ Mosquitto configuration complete!"
echo ""
echo "MQTT broker settings:"
echo "  Host: localhost (from Raspberry Pi) or raspberrypi (from network)"
echo "  Port: 1883"
echo "  User: $MQTT_USER"
echo "  Password: [hidden]"
echo ""
echo "Update your data/configuration.yaml to use:"
echo "  mqtt:"
echo "    server: mqtt://mosquitto:1883"
echo "    user: $MQTT_USER"
echo "    password: $MQTT_PASSWORD"
echo ""

