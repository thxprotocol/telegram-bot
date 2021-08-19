import logging

from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup
from telegram import ReplyKeyboardMarkup
from telegram import ReplyKeyboardRemove
from telegram import Update
from telegram.ext import CallbackContext
from telegram.ext import ConversationHandler
from telegram.utils import helpers


logger = logging.getLogger(__name__)


ADMIN_ROLES = ["creator", "administrator"]
CLIENT_ID, CLIENT_SECRET = range(2)


def setup(update: Update, context: CallbackContext) -> None:
    bot = context.bot
    chat_member_status = bot.get_chat_member(
        update.effective_chat.id, update.effective_user.id
    ).status
    if chat_member_status not in ADMIN_ROLES:
        update.message.reply_text("You are not admin of the chat. You can't configure this bot")
    url = helpers.create_deep_linked_url(bot.username, str(update.effective_chat.id))
    text = "Let's setup stuff:\n\n" + url
    update.message.reply_text(text)


def start_setting_channel(update: Update, context: CallbackContext) -> int:
    bot = context.bot
    chat_member_status = bot.get_chat_member(
        int(context.args[0]), update.effective_user.id
    ).status
    if chat_member_status not in ADMIN_ROLES:
        update.message.reply_text("You are not admin of the chat. You can't configure this bot")

    update.message.reply_text(
        "Let's set client_id to be used for THX API"
    )

    return CLIENT_ID


def client_id(update: Update, context: CallbackContext) -> int:
    logger.info(f"Client id is {update.message.text}")
    update.message.reply_text(
        "Good, now let's set client secret. Don't worry, I will keep it secret 🤐"
    )
    return CLIENT_SECRET


def client_secret(update: Update, context: CallbackContext) -> int:
    logger.info(f"Client id is {update.message.text}")
    update.message.reply_text(
        "Nice! You are all set to use THX now!"
    )
    return ConversationHandler.END


def cancel_setting_thx_bot(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info(f"User {user.first_name} canceled the conversation.")
    update.message.reply_text(
        'Bye! I hope we can talk again some day.', reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END
