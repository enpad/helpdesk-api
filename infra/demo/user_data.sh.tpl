#!/bin/bash
set -euxo pipefail

dnf install -y python3.11 python3.11-pip tar gzip

mkdir -p /opt/helpdesk-api
aws s3 cp "s3://${bucket}/${key}" /opt/helpdesk-api/release.tar.gz --region "${region}"
tar xzf /opt/helpdesk-api/release.tar.gz -C /opt/helpdesk-api

python3.11 -m venv /opt/helpdesk-api/venv
/opt/helpdesk-api/venv/bin/pip install --no-cache-dir -r /opt/helpdesk-api/infra/demo/requirements-runtime.txt

cat > /etc/systemd/system/helpdesk-api.service <<'UNIT'
[Unit]
Description=Helpdesk API course demo
After=network.target

[Service]
WorkingDirectory=/opt/helpdesk-api
Environment=HELPDESK_HOST=0.0.0.0
Environment=HELPDESK_PORT=8000
ExecStart=/opt/helpdesk-api/venv/bin/python run.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
UNIT

systemctl daemon-reload
systemctl enable --now helpdesk-api
