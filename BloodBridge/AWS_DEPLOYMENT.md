# AWS EC2 and RDS Deployment Guide

## 1. Create AWS RDS MySQL

1. Open AWS RDS and create a MySQL database.
2. Choose a free-tier or production instance size.
3. Set database name to `bloodbridge`.
4. Save the master username, password, and RDS endpoint.
5. Place RDS in the same VPC as your EC2 instance.
6. In the RDS security group, allow inbound MySQL `3306` only from the EC2 security group.

Load the schema from your machine or EC2:

```bash
mysql -h YOUR_RDS_ENDPOINT -u admin -p < database.sql
```

## 2. Create AWS EC2 Ubuntu Instance

1. Launch Ubuntu 22.04 or 24.04.
2. Security group inbound rules:
   - SSH `22` from your IP.
   - HTTP `80` from the internet.
   - HTTPS `443` from the internet if TLS is configured.
   - App test port `5000` only from your IP during development.
3. SSH into EC2.

```bash
ssh -i your-key.pem ubuntu@YOUR_EC2_PUBLIC_IP
```

## 3. Install System Packages

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git mysql-client nginx
```

## 4. Clone GitHub Repository

```bash
git clone https://github.com/YOUR_USERNAME/BloodBridge.git
cd BloodBridge
```

## 5. Configure Environment

```bash
cp .env.example .env
nano .env
```

Set these values:

```bash
SECRET_KEY=your-long-random-production-secret
MYSQL_HOST=your-rds-endpoint.amazonaws.com
MYSQL_PORT=3306
MYSQL_USER=admin
MYSQL_PASSWORD=your-password
MYSQL_DB=bloodbridge
LOW_STOCK_THRESHOLD=10
```

## 6. Install Python Dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 7. Test Flask on EC2

```bash
export FLASK_APP=app.py
flask run --host=0.0.0.0 --port=5000
```

Visit `http://YOUR_EC2_PUBLIC_IP:5000`.

## 8. Run with Gunicorn

```bash
source .venv/bin/activate
gunicorn --bind 127.0.0.1:8000 wsgi:app
```

## 9. Create systemd Service

Create `/etc/systemd/system/bloodbridge.service`.

```ini
[Unit]
Description=BloodBridge Flask App
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/BloodBridge
EnvironmentFile=/home/ubuntu/BloodBridge/.env
ExecStart=/home/ubuntu/BloodBridge/.venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 wsgi:app
Restart=always

[Install]
WantedBy=multi-user.target
```

Start it:

```bash
sudo systemctl daemon-reload
sudo systemctl enable bloodbridge
sudo systemctl start bloodbridge
sudo systemctl status bloodbridge
```

## 10. Configure Nginx Reverse Proxy

Create `/etc/nginx/sites-available/bloodbridge`.

```nginx
server {
    listen 80;
    server_name YOUR_DOMAIN_OR_EC2_PUBLIC_IP;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable and restart:

```bash
sudo ln -s /etc/nginx/sites-available/bloodbridge /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 11. Optional HTTPS

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

## 12. Notification Upgrades

- Replace `utils/notifications.py` email logging with AWS SES.
- Replace the SMS placeholder with AWS SNS or Twilio.
- Keep notification failures non-blocking so emergency request creation still succeeds.

