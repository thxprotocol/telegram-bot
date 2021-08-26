from telegram import Update
from telegram.ext import CallbackContext


def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("""
🤖     🤖     🤖
*Admin Actions:*
Connect your channel to work with THX API
\/register\_channel
Rewards menu, to view and set rewards for your channel
\/rewards

*If you are channel user:*
For signup:
\/create\_wallet
Send a one\-time login link for you wallet\(after signup is completed\)
_Make sure to link your new wallet address with_ \/update\_wallet
\/login\_wallet
""", parse_mode='MarkdownV2')
