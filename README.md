# Yandex.Lyceum.Cloud

Installing and running:
* install nginx python3 python3-pip systemctl
* pip3 install -r waitress/requirements.txt
* copy lavaland.service to /etc/systemd/system/
* copy nginx.conf to /etc/nginx/
* copy ssl certificates to /etc/nginx/ssl
* systemctl daemon-reload
* systemctl start lavaland.service
* systemctl enable lavaland.service
* systemctl start nginx.service
* systemctl enable nginx.service

Running without nginx:
* cd waitress
* pip3 install -r requirements.txt
* python3 wsgi.py
