git clone :
<br />
install python3
<br />
python3 -m venv ~/deploy_bot_venv
<br />
source ~/deploy_bot_venv/bin/activate
<br />
pip install --upgrade pip
<br />
pip install python-telegram-bot paramiko
<br />

 Systemd config :
 <br />
  nano /etc/systemd/system/deploybot.service
```
[Unit]
Description=Telegram Deploy Bot
After=network.target

[Service]
User=root
WorkingDirectory=/var/www/Tools-deployment
ExecStart=/root/deploy_bot_venv/bin/python /var/www/Tools-deployment/python-telegram-bot.py
Restart=always
RestartSec=10
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
```
#service systemd
<br />
sudo systemctl restart deploybot.service
<br />
 sudo systemctl daemon-reload
 <br />
 sudo systemctl start deploybot.service
 <br />
 sudo systemctl enable deploybot.service 

