git pull
pip3 install -r ./python/requirements.txt
sudo systemctl daemon-reload
sudo systemctl restart nginx.service lavaland.service
