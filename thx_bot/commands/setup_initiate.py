import logging

from telegram import Update
from telegram.constants import CHATMEMBER_ADMINISTRATOR
from telegram.constants import CHATMEMBER_CREATOR
from telegram.ext import CallbackContext
from telegram.utils import helpers

logger = logging.getLogger(__name__)


ADMIN_ROLES = [CHATMEMBER_CREATOR, CHATMEMBER_ADMINISTRATOR]
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
