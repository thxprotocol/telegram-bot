import os

from telegram import Update
from telegram.ext import CallbackContext
from telegram.ext import CommandHandler
from telegram.ext import ConversationHandler
from telegram.ext import Filters
from telegram.ext import MessageHandler
from telegram.ext import Updater

from thx_bot.commands.help_command import help_command
from thx_bot.commands.setup_channel import CLIENT_ID
from thx_bot.commands.setup_channel import CLIENT_SECRET
from thx_bot.commands.setup_channel import cancel_setting_thx_bot
from thx_bot.commands.setup_channel import client_id
from thx_bot.commands.setup_channel import client_secret
from thx_bot.commands.setup_channel import setup
from thx_bot.commands.setup_channel import start_setting_channel
from thx_bot.models.channels import Channel
from thx_bot.models.users import User
from thx_bot.services.thx_api_client import get_api_token
from thx_bot.services.thx_api_client import get_asset_pool_info
from thx_bot.services.thx_api_client import signup_user


def main() -> None:
    updater = Updater(os.getenv("BOT_TOKEN"))
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("setup", setup))
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start_setting_channel)],
        states={
            CLIENT_ID: [MessageHandler(Filters.text & ~Filters.command, client_id)],
            CLIENT_SECRET: [MessageHandler(Filters.text & ~Filters.command, client_secret)],
        },
        fallbacks=[CommandHandler('cancel', cancel_setting_thx_bot)],
    )
    dispatcher.add_handler(conv_handler)
    user = User({
        "email": "asdasdasd@gmail.com",
        "password": "qwerty12345"
    })
    channel = Channel({
        "pool_address": "0x4A986af8C3A1b94eF89Effb2B1f1870fFff97d18",
        "client_id": "CsunHOIB8TuaprHzPq6jg",
        "client_secret": "CcOwmr",
    })
    # get_asset_pool_info(channel)
    # signup_user(user, channel)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
