from functools import wraps

from telegram import Update
from telegram.constants import CHATMEMBER_MEMBER
from telegram.constants import CHAT_GROUP
from telegram.constants import CHAT_PRIVATE
from telegram.ext import CallbackContext

from thx_bot.constants import ADMIN_ROLES
from thx_bot.models.channels import Channel

NOT_ADMIN_TEXT = """
💬  You are not admin of the chat our group_id context is missing. 
Please go to the channel you want to setup and hit /setup there!
"""

NOT_CHAT_MEMBER_TEST = """
❌ Something went wrong! You cannot use THX integration because it appears that you are not channel
member. Please, contact your chat admin for help!
"""

NOT_PRIVATE_CHAT_TEXT = """
⛔️You can use this command only in a private chat with the bot for security reasons!
"""


CHAT_NOT_CONFIGURED = """
⛔️Chat is not yet configured or you were not redirected here from chat. 
Navigate to your chat and hit /setup to be redirected here.
If chat is not configured, ask your chat admin to do it!
"""


def only_chat_admin(f):
    @wraps(f)
    def wrapper(update: Update, context: CallbackContext):
        if update.effective_chat.type == CHAT_GROUP:
            chat_id = update.effective_chat.id
        else:
            chat_id = context.user_data.get('channel_id')

        if not chat_id:
            update.message.reply_text(NOT_ADMIN_TEXT)
            return

        chat_member_status = context.bot.get_chat_member(
            int(chat_id), update.effective_user.id).status
        if chat_member_status not in ADMIN_ROLES:
            update.message.reply_text(NOT_ADMIN_TEXT)
            return
        return f(update, context)
    return wrapper


def only_chat_user(f):
    @wraps(f)
    def wrapper(update: Update, context: CallbackContext):
        if update.effective_chat.type == CHAT_GROUP:
            chat_id = update.effective_chat.id
        else:
            chat_id = context.user_data.get('channel_id')

        if not chat_id:
            update.message.reply_text(NOT_CHAT_MEMBER_TEST)
            return

        chat_member_status = context.bot.get_chat_member(
            int(chat_id), update.effective_user.id).status
        allowed_roles = [*ADMIN_ROLES]
        allowed_roles.append(CHATMEMBER_MEMBER)
        if chat_member_status not in allowed_roles:
            update.message.reply_text(NOT_CHAT_MEMBER_TEST)
            return
        return f(update, context)
    return wrapper


def only_in_private_chat(f):
    @wraps(f)
    def wrapper(update: Update, context: CallbackContext):
        """
        Allow to setup bot only in a private channel.
        """
        if not update.effective_chat.type == CHAT_PRIVATE:
            update.message.reply_text(NOT_PRIVATE_CHAT_TEXT)
            return
        return f(update, context)
    return wrapper


def only_if_channel_configured(f):
    @wraps(f)
    def wrapper(update: Update, context: CallbackContext):
        """
        Allow to manipulate with configuration only in case admin has already set up channel
        """
        channel = Channel.collection.find_one({'channel_id': context.user_data.get('channel_id')})
        is_channel_set = all([
            channel.get('client_id'), channel.get('client_secret'), channel.get('pool_address')
        ]) if channel else False
        if not channel or not is_channel_set:
            update.message.reply_text(CHAT_NOT_CONFIGURED)
            return
        return f(update, context)
    return wrapper
