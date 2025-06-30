#!/bin/bash

# =============================
# Django Deployment Shell Script
# =============================

# Exit on any error
set -e

# ----- Configuration -----
PROJECT_NAME="allistic_server"
# GIT_TOKEN="ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
# GIT_REPO="https://cs-prashant-dev:$GIT_TOKEN@github.com/cs-prashant-dev/yale_api.git"
GIT_REPO="https://github.com/cs-prashant-dev/yale_api.git"  # Replace with your repo
PROJECT_DIR="/home/ubuntu/$PROJECT_NAME"
PYTHON_VERSION="python3.11"
REQUIRED_PYTHON_VERSION="3.11"
DJANGO_PORT="8000"
DOMAIN_NAME="yourdomain.com"  # For nginx setup
# --------------------------

echo "Updating system packages..."
sudo apt update && sudo apt upgrade -y

echo "Checking if Python $REQUIRED_PYTHON_VERSION is installed..."

# Check if Python version exists
if command -v $PYTHON_VERSION >/dev/null 2>&1; then
    INSTALLED_PYTHON_VERSION=$($PYTHON_VERSION --version 2>&1 | awk '{print $2}' | cut -d '.' -f1,2)
    if [[ "$INSTALLED_PYTHON_VERSION" == "$REQUIRED_PYTHON_VERSION" ]]; then
        echo "✅ Python $REQUIRED_PYTHON_VERSION is already installed."
    else
        echo "❌ Python $PYTHON_VERSION is not the correct version. Found Python $INSTALLED_PYTHON_VERSION."
        exit 1
    fi
else
    echo "❌ Python $PYTHON_VERSION not found. Please install it manually."
    exit 1
fi

echo "Installing required packages (excluding Python)..."
sudo apt install -y python3-pip nginx git

echo "Cloning Django project..."
git clone $GIT_REPO $PROJECT_DIR

cd $PROJECT_DIR

echo "Creating virtual environment..."
$PYTHON_VERSION -m venv venv
source venv/bin/activate

echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Running Django migrations..."
python manage.py migrate

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Testing Gunicorn..."
gunicorn --bind 0.0.0.0:$DJANGO_PORT $PROJECT_NAME.wsgi:application --daemon

echo "Creating Gunicorn service..."
sudo tee /etc/systemd/system/gunicorn.service > /dev/null <<EOF
[Unit]
Description=gunicorn daemon for $PROJECT_NAME
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=$PROJECT_DIR
ExecStart=$PROJECT_DIR/venv/bin/gunicorn --access-logfile - --workers 3 --bind unix:$PROJECT_DIR/$PROJECT_NAME.sock $PROJECT_NAME.wsgi:application

[Install]
WantedBy=multi-user.target
EOF

echo "Starting and enabling Gunicorn..."
sudo systemctl start gunicorn
sudo systemctl enable gunicorn

echo "Configuring Nginx..."
sudo tee /etc/nginx/sites-available/$PROJECT_NAME > /dev/null <<EOF
server {
    listen 80;
    server_name $DOMAIN_NAME;

    location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ {
        root $PROJECT_DIR;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:$PROJECT_DIR/$PROJECT_NAME.sock;
    }
}
EOF

sudo ln -s /etc/nginx/sites-available/$PROJECT_NAME /etc/nginx/sites-enabled

echo "Testing Nginx configuration..."
sudo nginx -t

echo "Restarting Nginx..."
sudo systemctl restart nginx

echo "Allowing HTTP through firewall..."
sudo ufw allow 'Nginx Full'

echo "Deployment completed successfully!"
echo "Your Django project is now running at http://$DOMAIN_NAME"
