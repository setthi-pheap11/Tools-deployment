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
CHOOSING_ENV, TYPING_BRANCH = range(2)

# SSH config
SSH_HOST = 'your server'
SSH_USER = 'root'
SSH_KEY_PATH = os.path.expanduser('~/.ssh/id_rsa_bot')  # private key path

# Authorized Telegram user IDs (replace with yours)
AUTHORIZED_USERS = {123456789}  # Put your Telegram user ID here

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in AUTHORIZED_USERS:
        await update.message.reply_text("❌ You are not authorized to use this bot.")
        return ConversationHandler.END

    keyboard = [['Deploy Dev Server', 'Deploy Staging Server']]
    await update.message.reply_text(
        "Choose environment to deploy:",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True),
    )
    return CHOOSING_ENV

async def choosing_env(update: Update, context: ContextTypes.DEFAULT_TYPE):
    env_text = update.message.text.lower()
    if 'dev' in env_text:
        context.user_data['env'] = 'dev'
    elif 'staging' in env_text:
        context.user_data['env'] = 'staging'
    else:
        await update.message.reply_text("⚠️ Please choose a valid environment.")
        return CHOOSING_ENV

    await update.message.reply_text(
        f"Type the branch name to deploy to **{context.user_data['env']}** server:",
        parse_mode='Markdown'
    )
    return TYPING_BRANCH

def ssh_run_command(env: str, branch: str):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(SSH_HOST, username=SSH_USER, key_filename=SSH_KEY_PATH, timeout=10)

        deploy_dir = '/var/www/scholarar'

        cmd = (
            f"cd {deploy_dir} && "
            f"sudo git fetch origin && "
            f"sudo git checkout {branch} && "
            f"sudo git pull origin {branch}"
        )

        stdin, stdout, stderr = ssh.exec_command(cmd, timeout=120)
        out = stdout.read().decode()
        err = stderr.read().decode()

        ssh.close()
        return out, err

    except Exception as e:
        return "", f"SSH error: {e}"

async def typing_branch(update: Update, context: ContextTypes.DEFAULT_TYPE):
    branch = update.message.text.strip()
    if not branch:
        await update.message.reply_text("⚠️ Branch name cannot be empty. Please type the branch name:")
        return TYPING_BRANCH

    env = context.user_data['env']

    await update.message.reply_text(f"🚀 Deploying branch '{branch}' to **{env}** server... Please wait.", parse_mode='Markdown')

    out, err = ssh_run_command(env, branch)

    if err:
        await update.message.reply_text(f"❌ Deployment failed:\n```\n{err}\n```", parse_mode='Markdown')
    else:
        await update.message.reply_text(f"✅ Deployment succeeded:\n```\n{out}\n```", parse_mode='Markdown')

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚫 Deployment canceled.")
    return ConversationHandler.END

def main():
    TELEGRAM_BOT_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN_HERE'

    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING_ENV: [MessageHandler(filters.TEXT & ~filters.COMMAND, choosing_env)],
            TYPING_BRANCH: [MessageHandler(filters.TEXT & ~filters.COMMAND, typing_branch)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    application.add_handler(conv_handler)

    print("Bot started...")
    application.run_polling()

if __name__ == '__main__':
    main()
