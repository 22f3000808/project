#!/bin/bash
# Install as a systemd user service (Linux)
SERVICE_FILE="$HOME/.config/systemd/user/sysutil.service"

mkdir -p "$(dirname "$SERVICE_FILE")"

cat > "$SERVICE_FILE" <<EOF
[Unit]
Description=SysUtil Agent

[Service]
ExecStart=$(which python3) $(pwd)/main.py --background --interval 30
Restart=always

[Install]
WantedBy=default.target
EOF

systemctl --user daemon-reload
systemctl --user enable --now sysutil
echo "Service installed and started."
