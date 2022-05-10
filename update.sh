git pull
pip3 install -r ./python/requirements.txt > /dev/null
sudo systemctl daemon-reload
sudo systemctl restart lavaland.service
