#!/bin/bash

sudo apt install -y gconf-service libasound2 libatk1.0-0 libc6 libcairo2 libcups2 libdbus-1-3 libexpat1 libfontconfig1 libgcc1 libgconf-2-4 libgdk-pixbuf2.0-0 libglib2.0-0 libgtk-3-0 libnspr4 libpango-1.0-0 libpangocairo-1.0-0 libstdc++6 libx11-6 libx11-xcb1 libxcb1 libxcomposite1 libxcursor1 libxdamage1 libxext6 libxfixes3 libxi6 libxrandr2 libxrender1 libxss1 libxtst6 ca-certificates fonts-liberation libappindicator1 libnss3 lsb-release xdg-utils wget rabbitmq-server redis-server

source env/bin/activate

pip install -r requirements.txt
pip install --upgrade --force-reinstall git+ssh://git@gitlab.com/ofirio-realestate/ofirio-common.git

# Place build info to a file
(echo -n `git branch --show-current`; echo -n " "; echo -n `git rev-parse HEAD`) > buildinfo

echo 'from django.core.cache import cache; cache.clear()' | python manage.py shell

python manage.py collectstatic --noinput
python manage.py migrate --noinput

sudo supervisorctl restart all
deactivate

sudo systemctl restart supervisor
sudo systemctl restart gunicorn
sudo systemctl restart gunicorn_stage || true
sudo systemctl restart gunicorn_invest || true
