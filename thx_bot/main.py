import os

from telegram import Update
from telegram.ext import CallbackContext
from telegram.ext import CommandHandler
from telegram.ext import Updater
from telegram.utils import helpers

from thx_bot.commands.get_member import get_member_info
from thx_bot.commands.help_command import HELP_TEMPLATE
from thx_bot.commands.help_command import help_command
from thx_bot.commands.login_wallet import login_wallet
from thx_bot.integration_conversations import create_wallet_conversation
from thx_bot.integration_conversations import register_channel_conversation
from thx_bot.integration_conversations import rewards_conversation
from thx_bot.integration_conversations import update_wallet_conversation
from thx_bot.kyu_conversation import kyu_conversation
from thx_bot.models.channels import Channel
from thx_bot.models.know_your_user import KnowYourUser
from thx_bot.models.users import User


def setup(update: Update, context: CallbackContext) -> None:
    bot = context.bot

    url = helpers.create_deep_linked_url(bot.username, str(update.effective_chat.id))
    text = "If you are admin, you might want to setup THX API integration.\n" \
           "If you are user, you might want to setup you account so you can collect rewards.\n\n" \
           "Let's setup stuff:\n" + url
    update.message.reply_text(text)


def start(update: Update, context: CallbackContext) -> None:
    if context.args:
        context.user_data['channel_id'] = context.args[0]
    update.message.reply_text(HELP_TEMPLATE, parse_mode='MarkdownV2')


def main() -> None:
    updater = Updater(os.getenv("BOT_TOKEN"))
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("help", help_command))

    dispatcher.add_handler(register_channel_conversation)
    dispatcher.add_handler(rewards_conversation)
    dispatcher.add_handler(create_wallet_conversation)
    dispatcher.add_handler(update_wallet_conversation)
    dispatcher.add_handler(kyu_conversation)
    dispatcher.add_handler(CommandHandler("setup", setup))
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("login_wallet", login_wallet))
    dispatcher.add_handler(CommandHandler("get_my_info", get_member_info))
    # channels = Channel.collection.remove({})
    # users = User.collection.remove({})
    channels = Channel.collection.find({})
    users = User.collection.find({})
    kyu = KnowYourUser.collection.find({})
    print(list(users))
    print(list(channels))
    print(list(kyu))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
