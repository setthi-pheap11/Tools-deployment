git clone :
\n install python3
python3 -m venv ~/deploy_bot_venv
source ~/deploy_bot_venv/bin/activate
pip install --upgrade pip
pip install python-telegram-bot paramiko

 Systemd config :
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
sudo systemctl restart deploybot.service
 sudo systemctl daemon-reload
 sudo systemctl start deploybot.service
 sudo systemctl enable deploybot.service 
