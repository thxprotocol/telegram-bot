import os

from telegram import Update
from telegram.ext import CallbackContext
from telegram.ext import CommandHandler
from telegram.ext import ConversationHandler
from telegram.ext import Filters
from telegram.ext import MessageHandler
from telegram.ext import Updater
from telegram.utils import helpers

from thx_bot.commands import CHOOSING
from thx_bot.commands import CHOOSING_SIGNUP
from thx_bot.commands import TYPING_REPLY
from thx_bot.commands import TYPING_REPLY_SIGNUP
from thx_bot.commands.create_wallet import received_information_signup
from thx_bot.commands.create_wallet import regular_choice_signup
from thx_bot.commands.create_wallet import done_signup
from thx_bot.commands.help_command import help_command
from thx_bot.commands.register_channel import done_channel
from thx_bot.commands.register_channel import received_information_channel
from thx_bot.commands.register_channel import regular_choice_channel
from thx_bot.commands.register_channel import start_setting_channel
from thx_bot.commands.create_wallet import start_creating_wallet
from thx_bot.models.channels import Channel
from thx_bot.models.users import User


def setup(update: Update, context: CallbackContext) -> None:
    bot = context.bot

    url = helpers.create_deep_linked_url(bot.username, str(update.effective_chat.id))
    text = "If you are admin, you might want to setup THX API integration.\n" \
           "If you are user, you might want to setup you account so you can collect rewards.\n\n" \
           "Let's setup stuff:\n" + url
    update.message.reply_text(text)


def start(update: Update, context: CallbackContext) -> None:
    reply_text = ("Hi, if you want to setup channel with THX API:\n /register_channel\n\n"
                  "If you want to signup:\n /create_wallet")
    if context.args:
        context.user_data['channel_id'] = context.args[0]
    update.message.reply_text(reply_text)


def main() -> None:
    updater = Updater(os.getenv("BOT_TOKEN"))
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("help", help_command))

    register_channel_conversation = ConversationHandler(
        entry_points=[CommandHandler('register_channel', start_setting_channel)],  # noqa
        states={  # noqa
            CHOOSING: [
                MessageHandler(
                    Filters.regex('^(Client id|Client secret|Pool address)$'), regular_choice_channel
                ),
            ],
            TYPING_REPLY: [
                MessageHandler(
                    Filters.text & ~(Filters.command | Filters.regex('^Done$')),
                    received_information_channel,
                )
            ],
        },
        fallbacks=[MessageHandler(Filters.regex('^Done$'), done_channel)],  # noqa
        name="register_channel",
        persistent=False,
    )
    create_wallet_conversation = ConversationHandler(
        entry_points=[CommandHandler('create_wallet', start_creating_wallet)],  # noqa
        states={  # noqa
            CHOOSING_SIGNUP: [
                MessageHandler(
                    Filters.regex('^(Email|Password)$'), regular_choice_signup
                ),
            ],
            TYPING_REPLY_SIGNUP: [
                MessageHandler(
                    Filters.text & ~(Filters.command | Filters.regex('^Done$')),
                    received_information_signup,
                )
            ],
        },
        fallbacks=[MessageHandler(Filters.regex('^Done$'), done_signup)],  # noqa
        name="create_wallet",
        persistent=False,
    )
    dispatcher.add_handler(register_channel_conversation)
    dispatcher.add_handler(create_wallet_conversation)
    dispatcher.add_handler(CommandHandler("setup", setup))
    dispatcher.add_handler(CommandHandler("start", start))
    channels = Channel.collection.find({})
    users = User.collection.find({})
    print(list(channels))
    print(list(users))
    # get_asset_pool_info(channel)
    # signup_user(user, channel)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
