import os

from telegram import Update
from telegram.ext import CallbackContext
from telegram.ext import CommandHandler
from telegram.ext import ConversationHandler
from telegram.ext import Filters
from telegram.ext import MessageHandler
from telegram.ext import Updater
from telegram.utils import helpers

from thx_bot.commands.help_command import help_command
from thx_bot.commands.register_channel import CHOOSING
from thx_bot.commands.register_channel import TYPING_REPLY
from thx_bot.commands.register_channel import done
from thx_bot.commands.register_channel import received_information
from thx_bot.commands.register_channel import regular_choice
from thx_bot.commands.register_channel import start_setting_channel
from thx_bot.models.channels import Channel
from thx_bot.models.users import User


def setup(update: Update, context: CallbackContext) -> None:
    bot = context.bot

    url = helpers.create_deep_linked_url(bot.username, str(update.effective_chat.id))
    text = "Let's setup stuff:\n\n" + url
    update.message.reply_text(text)


def start(update: Update, context: CallbackContext) -> None:
    reply_text = ("Hi, if you want to setup channel with THX API:\n /register_channel\n\n"
                  "If you want to signup:\n /signup")
    if context.args:
        context.user_data['channel_id'] = context.args[0]
    update.message.reply_text(reply_text)


def main() -> None:
    updater = Updater(os.getenv("BOT_TOKEN"))
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("help", help_command))

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('register_channel', start_setting_channel)],  # noqa
        states={  # noqa
            CHOOSING: [
                MessageHandler(
                    Filters.regex('^(Client id|Client secret|Pool address)$'), regular_choice
                ),
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
    dispatcher.add_handler(CommandHandler("setup", setup))
    dispatcher.add_handler(CommandHandler("start", start))
    user = User({
        "email": "asdasdasd@gmail.com",
        "password": "qwerty12345"
    })
    channels = Channel.collection.find({})
    print(list(channels))
    # get_asset_pool_info(channel)
    # signup_user(user, channel)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
