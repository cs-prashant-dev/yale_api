PROJECT_NAME="allistic_server"
BRANCH="v1"
SYSTEM_USER="allistic_app_django"
PROJECT_DIR="/home/$SYSTEM_USER/$PROJECT_NAME"

cd "$PROJECT_DIR"
git fetch --all
git reset --hard origin/"$BRANCH"
source venv/bin/activate
pip install -r requirements.txt
deactivate

sudo systemctl daemon-reload
sudo systemctl restart gunicorn_"$PROJECT_NAME".service
sudo systemctl restart gunicorn_"$PROJECT_NAME".socket

sudo nginx -t && sudo systemctl reload nginx
