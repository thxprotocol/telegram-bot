import logging
from typing import Dict

from telegram import ReplyKeyboardMarkup
from telegram import ReplyKeyboardRemove
from telegram import Update
from telegram.constants import CHATMEMBER_ADMINISTRATOR
from telegram.constants import CHATMEMBER_CREATOR
from telegram.ext import CallbackContext
from telegram.ext import ConversationHandler

logger = logging.getLogger(__name__)


ADMIN_ROLES = [CHATMEMBER_CREATOR, CHATMEMBER_ADMINISTRATOR]
CLIENT_ID, CLIENT_SECRET = range(2)
CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(3)


reply_keyboard = [
    ['Client id', 'Client secret', 'Pool address'],
    ['Done'],
]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)


def facts_to_str(user_data: Dict[str, str]) -> str:
    """Helper function for formatting the gathered user info."""
    facts = [f'➡️{key} - {value}' for key, value in user_data.items()]
    return "\n".join(facts).join(['\n', '\n'])


def start(update: Update, context: CallbackContext) -> None:
    reply_text = ("Hi, if you want to setup channel with THX API: /start_setting_channel\n"
                  "If you want to signup: /signup")
    if context.args:
        context.user_data['channel_id'] = context.args[0]
    update.message.reply_text(reply_text)


def start_setting_channel(update: Update, context: CallbackContext) -> int:
    reply_text = "Please, fill all items to start using THX API in your channel"
    update.message.reply_text(reply_text, reply_markup=markup)

    return CHOOSING


def regular_choice(update: Update, context: CallbackContext) -> int:
    text = update.message.text.lower()
    if text == 'client id' or text == 'client secret' or text == 'pool address':
        bot = context.bot
        chat_member_status = bot.get_chat_member(
            int(context.user_data['channel_id']), update.effective_user.id
        ).status
        if chat_member_status not in ADMIN_ROLES:
            update.message.reply_text("You are not admin of the chat. You can't configure this bot")

    context.user_data['choice'] = text
    if context.user_data.get(text):
        reply_text = (
            f'Your {text}? I already know the following about that: {context.user_data[text]}'
        )
    else:
        reply_text = f'Your {text}? Yes, I would love to hear about that!'
    update.message.reply_text(reply_text)

    return TYPING_REPLY


def received_information(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    category = context.user_data['choice']
    context.user_data[category] = text.lower()
    del context.user_data['choice']

    update.message.reply_text(
        "Cool! Just so you know, this is what you already told me:"
        f"{facts_to_str(context.user_data)}"
        "You can change client or secret any time.",
        reply_markup=markup,
    )

    return CHOOSING


def done(update: Update, context: CallbackContext) -> int:
    if 'choice' in context.user_data:
        del context.user_data['choice']

    update.message.reply_text(
        f"I learned these facts about you: {facts_to_str(context.user_data)}Until next time!",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END
