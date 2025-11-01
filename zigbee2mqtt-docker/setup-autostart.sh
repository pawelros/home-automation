#!/bin/bash
# This script sets up zigbee2mqtt to auto-start on boot using systemd
# Run this on your Raspberry Pi after deploying zigbee2mqtt

set -e

INSTALL_DIR="${1:-$HOME/zigbee2mqtt}"
SERVICE_USER="${2:-$USER}"

echo "========================================="
echo "Setting up Zigbee2MQTT Auto-Start"
echo "========================================="
echo "Install directory: $INSTALL_DIR"
echo "Service user: $SERVICE_USER"
echo ""

# Check if directory exists
if [ ! -d "$INSTALL_DIR" ]; then
    echo "❌ Directory not found: $INSTALL_DIR"
    echo "Please deploy zigbee2mqtt first!"
    exit 1
fi

# Check if docker-compose.yml exists
if [ ! -f "$INSTALL_DIR/docker-compose.yml" ]; then
    echo "❌ docker-compose.yml not found in $INSTALL_DIR"
    exit 1
fi

echo "✓ Found zigbee2mqtt installation"

# Create systemd service file
echo "Creating systemd service..."
sudo tee /etc/systemd/system/zigbee2mqtt.service > /dev/null <<EOF
[Unit]
Description=Zigbee2MQTT Docker Container
Requires=docker.service
After=docker.service network-online.target
Wants=network-online.target

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=$INSTALL_DIR
ExecStart=/usr/bin/docker compose up -d
ExecStop=/usr/bin/docker compose down
ExecReload=/usr/bin/docker compose restart
User=$SERVICE_USER
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo "✓ Service file created"

# Reload systemd
echo "Reloading systemd..."
sudo systemctl daemon-reload

# Enable service
echo "Enabling auto-start..."
sudo systemctl enable zigbee2mqtt

# Start service now (if not already running)
echo "Starting service..."
sudo systemctl start zigbee2mqtt

# Show status
echo ""
echo "========================================="
echo "✓ Auto-start configured successfully!"
echo "========================================="
echo ""
echo "Service status:"
sudo systemctl status zigbee2mqtt --no-pager || true
echo ""
echo "Useful commands:"
echo "  sudo systemctl status zigbee2mqtt    # Check status"
echo "  sudo systemctl restart zigbee2mqtt   # Restart service"
echo "  sudo systemctl stop zigbee2mqtt      # Stop service"
echo "  sudo systemctl start zigbee2mqtt     # Start service"
echo "  sudo systemctl disable zigbee2mqtt   # Disable auto-start"
echo "  journalctl -u zigbee2mqtt -f         # View service logs"
echo ""

