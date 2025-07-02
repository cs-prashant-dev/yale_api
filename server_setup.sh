#!/bin/bash

# =============================
# Django Deployment Shell Script
# =============================
# https://www.digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-ubuntu#steps-to-setup-django-nginx-gunicorn
# Exit on any error
set -e

# ----- Configuration -----
PROJECT_NAME="allistic_server"
GIT_REPO="https://github.com/cs-prashant-dev/yale_api.git"
BRANCH="v1"
SYSTEM_USER="allistic_django"
PROJECT_DIR="/home/$SYSTEM_USER/$PROJECT_NAME"
PYTHON_VERSION="python3.12"
REQUIRED_PYTHON_VERSION="3.12"
DJANGO_PORT="8000"
DOMAIN_NAME="allistic3.cschat.confidosoft.in"  # For nginx setup
SLEEP_TIME=5
ENABLE_SSL="True"
ADMIN_EMAIL="prashant.prajapati@confidosoft.in"
# --------------------------

if ! id $SYSTEM_USER &>/dev/null; then
  echo "✅ Creating system user 'django'..."
  sudo adduser --system --group --home /home $SYSTEM_USER
  sudo usermod -aG www-data $SYSTEM_USER
fi

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
git clone -b "$BRANCH" --single-branch "$GIT_REPO" "$PROJECT_DIR"
cd $PROJECT_DIR

echo "Creating virtual environment..."
$PYTHON_VERSION -m venv venv
source venv/bin/activate

echo "Installing Python dependencies..."
pip install --upgrade pip
pip install Django gunicorn
pip install -r requirements.txt

# cd $PROJECT_DIR
echo "Running Django migrations..."
python manage.py migrate
sleep $SLEEP_TIME
# echo "Collecting static files..."
python manage.py collectstatic --noinput
sleep $SLEEP_TIME
# sudo ufw allow $DJANGO_PORT


deactivate

echo "Creating Gunicorn socket..."
sudo tee /etc/systemd/system/gunicorn_$PROJECT_NAME.socket > /dev/null <<EOF
[Unit]
Description=gunicorn socket

[Socket]
ListenStream=/run/gunicorn_$PROJECT_NAME.sock

[Install]
WantedBy=sockets.target
EOF

echo "Creating Gunicorn service..."
sudo tee /etc/systemd/system/gunicorn_$PROJECT_NAME.service > /dev/null <<EOF
[Unit]
Description=gunicorn daemon for $PROJECT_NAME
Requires=gunicorn_$PROJECT_NAME.socket
After=network.target nss-user-lookup.target

[Service]
User=$SYSTEM_USER
Group=www-data
WorkingDirectory=$PROJECT_DIR
ExecStart=$PROJECT_DIR/venv/bin/gunicorn \
  --access-logfile - \
  --workers 3 \
  --bind unix:/run/gunicorn_$PROJECT_NAME.sock \
  $PROJECT_NAME.wsgi:application

[Install]
WantedBy=multi-user.target
EOF

echo "Reloading systemd to register new service..."
sudo systemctl daemon-reload
sleep $SLEEP_TIME
echo "Gunicorn Socket Start..."
echo "Starting and enabling Gunicorn..."
sudo systemctl start gunicorn_$PROJECT_NAME.socket
sudo systemctl enable gunicorn_$PROJECT_NAME.socket

echo "Checking Gunicorn socket status..."
# file /run/gunicorn_$PROJECT_NAME.sock
# sudo journalctl -u gunicorn_$PROJECT_NAME.socket
sudo systemctl status gunicorn_$PROJECT_NAME.socket
sleep $SLEEP_TIME

sudo systemctl daemon-reload
sudo systemctl restart gunicorn_$PROJECT_NAME.socket
sleep $SLEEP_TIME

echo "Configuring Nginx..."
sudo tee /etc/nginx/sites-available/$DOMAIN_NAME > /dev/null <<EOF
server {
    listen 80;
    server_name $DOMAIN_NAME;

    location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ {
        root $PROJECT_DIR;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn_$PROJECT_NAME.sock;
    }
}
EOF

sudo ln -s /etc/nginx/sites-available/$DOMAIN_NAME /etc/nginx/sites-enabled
sudo rm -f /etc/nginx/sites-enabled/default
sudo systemctl reload nginx

echo "Testing Nginx configuration..."
sudo nginx -t
sleep $SLEEP_TIME

echo "Restarting Nginx..."
sudo systemctl restart nginx

echo "Allowing HTTP through firewall..."
# sudo ufw delete allow $DJANGO_PORT
sudo ufw allow 'Nginx Full'

# --- SSL with Certbot ---
if [ "$ENABLE_SSL" = "True" ]; then
  sudo apt install snapd -y
  sudo snap install core && sudo snap refresh core
  sudo snap install --classic certbot
  sudo certbot --nginx -d $DOMAIN_NAME --noninteractive --agree-tos --email $ADMIN_EMAIL --redirect
fi
echo "Deployment completed successfully!"
echo "Your Django project is now running at http://$DOMAIN_NAME"
