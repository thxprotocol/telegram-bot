import os

from telegram.ext import CommandHandler
from telegram.ext import ConversationHandler
from telegram.ext import Filters
from telegram.ext import MessageHandler
from telegram.ext import Updater

from thx_bot.commands.help_command import help_command
from thx_bot.commands.setup import CHOOSING
from thx_bot.commands.setup import TYPING_CHOICE
from thx_bot.commands.setup import TYPING_REPLY
from thx_bot.commands.setup import done
from thx_bot.commands.setup import received_information
from thx_bot.commands.setup import regular_choice
from thx_bot.commands.setup import start
from thx_bot.commands.setup import start_setting_channel
from thx_bot.commands.setup_initiate import setup
from thx_bot.models.channels import Channel
from thx_bot.models.users import User


def main() -> None:
    updater = Updater(os.getenv("BOT_TOKEN"))
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("setup", setup))

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start_setting_channel', start_setting_channel)],  # noqa
        states={  # noqa
            CHOOSING: [
                MessageHandler(
                    Filters.regex('^(Client id|Client secret|Pool address)$'), regular_choice
                ),
            ],
            TYPING_CHOICE: [
                MessageHandler(
                    Filters.text & ~(Filters.command | Filters.regex('^Done$')), regular_choice
                )
            ],
            TYPING_REPLY: [
                MessageHandler(
                    Filters.text & ~(Filters.command | Filters.regex('^Done$')),
                    received_information,
                )
            ],
        },
        fallbacks=[MessageHandler(Filters.regex('^Done$'), done)],  # noqa
        name="my_conversation",
        persistent=False,
    )

    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(CommandHandler("start", start))
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
