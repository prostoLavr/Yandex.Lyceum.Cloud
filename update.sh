git pull
pip3 install -r requirements.txt > /dev/null
sudo systemctl daemon-reload
sudo systemctl restart test_lavaland.service
