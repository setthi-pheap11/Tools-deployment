1.cd /usr/local/bin/
<br />
2.nano deploy_scholarar.sh
```
#!/bin/bash

ENV=$1   # dev or staging
BRANCH=$2

if [ "$ENV" == "dev" ]; then
  DIR="/var/www/scholarar"
elif [ "$ENV" == "staging" ]; then
  DIR="/var/www/scholarar-staging"
else
  echo "Invalid environment"
  exit 1
fi

cd $DIR || exit 1
sudo -i
git fetch origin
git checkout $BRANCH
git pull origin $BRANCH
# Add more deploy steps here if you want (npm install, composer install, etc.)

echo "Deploy complete on $ENV with branch $BRANCH"

```

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
<br />
Python Code:
```
import os
import paramiko
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

# Conversation states
CHOOSING_ENV = 0  # Only one step now

# SSH config
SSH_HOST = '128.199.91.247'
SSH_USER = 'root'
SSH_KEY_PATH = os.path.expanduser('~/.ssh/id_rsa_bot')  # private key path

# Authorized Telegram user IDs (replace with yours)
AUTHORIZED_USERS = {721177574,1145778529,1103801424,1132241019,1065582966}  # Put your Telegram user ID here

# Fixed branch per environment
FIXED_BRANCHES = {
    'dev': 'develop',
    'staging': 'staging',
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in AUTHORIZED_USERS:
        await update.message.reply_text("❌ You are not authorized to use this bot.")
        return ConversationHandler.END

    keyboard = [['Deploy Dev Server', 'Deploy Staging Server']]
    await update.message.reply_text(
        "Choose environment to deploy(server ដែរត្រូវDeploy):",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True),
    )
    return CHOOSING_ENV

async def choosing_env(update: Update, context: ContextTypes.DEFAULT_TYPE):
    env_text = update.message.text.lower()
    if 'dev' in env_text:
        env = 'dev'
    elif 'staging' in env_text:
        env = 'staging'
    else:
        await update.message.reply_text("⚠️ Please choose a valid environment.")
        return CHOOSING_ENV

    branch = FIXED_BRANCHES[env]
    await update.message.reply_text(
        f"🚀 Deploying fixed branch '{branch}' to **{env}** server... Please wait.",
        parse_mode='Markdown'
    )

    out, err = ssh_run_command(env, branch)

    if err:
        await update.message.reply_text(f"❌ Deployment failed:\nក្នុងករណីPull success តែលោត status failedត្រូវចុច Deploy ម្ដងទៀត\nFor Staging server : https://staging.sandbox.scholarar.com/admin/login\nFor Dev server : https://dev.sandbox.scholarar.com/admin/login\n```\n{err}\n```", parse_mode='Markdown')
    else:
        await update.message.reply_text(f"✅ Deployment succeeded:\nFor Staging server : https://staging.sandbox.scholarar.com/admin/login\nFor Dev server : https://dev.sandbox.scholarar.com/admin/login\n```\n{out}\n```", parse_mode='Markdown')

    return ConversationHandler.END

def ssh_run_command(env: str, branch: str):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(SSH_HOST, username=SSH_USER, key_filename=SSH_KEY_PATH, timeout=10)

        if env == 'dev':
            deploy_dir = '/var/www/scholarar'
        elif env == 'staging':
            deploy_dir = '/var/www/scholarar-staging'
        else:
            deploy_dir = '/var/www/scholarar'

        cmd = (
            f"cd {deploy_dir} && "
            f"sudo git pull && "
            f"sudo php artisan migrate --force && "
            f"sudo php artisan optimize:clear"

        )


        stdin, stdout, stderr = ssh.exec_command(cmd, timeout=120)
        out = stdout.read().decode()
        err = stderr.read().decode()

        ssh.close()
        return out, err

    except Exception as e:
        return "", f"SSH error: {e}"

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚫 Deployment canceled.")
    return ConversationHandler.END

def main():
    TELEGRAM_BOT_TOKEN = '7705607267:AAHh_Rg7N_Sw5fUEgyOHu2FPIdYk044oNxw'

    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING_ENV: [MessageHandler(filters.TEXT & ~filters.COMMAND, choosing_env)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    application.add_handler(conv_handler)

    print("Bot started...")
    application.run_polling()

if __name__ == '__main__':
    main()
```
<br />
config telegrambot use ```@BotFather```
<br />
after create a bot need bot token to use on python code .
<br />
add bot to telegram group and  add user telegram id to code .
how to get user telegram id ```@userinfobot```
<br />
how to use this bot just /start to use this bot first

