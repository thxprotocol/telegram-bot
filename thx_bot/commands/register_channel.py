import logging
from typing import Dict

from pymongo import ReturnDocument
from telegram import ReplyKeyboardMarkup
from telegram import ReplyKeyboardRemove
from telegram import Update
from telegram.ext import CallbackContext
from telegram.ext import ConversationHandler

from thx_bot.models.channels import Channel
from thx_bot.validators import only_chat_admin
from thx_bot.validators import only_in_private_chat

logger = logging.getLogger(__name__)


CLIENT_ID, CLIENT_SECRET = range(2)
CHOOSING, TYPING_REPLY = range(2)

OPTION_CLIENT_ID = "Client id"
OPTION_CLIENT_SECRET = "Client secret"
OPTION_POOL_ADDRESS = "Pool address"
REPLY_KEYBOARD = [
    [OPTION_CLIENT_ID, OPTION_CLIENT_SECRET, OPTION_POOL_ADDRESS],
    ['Done'],
]
REPLY_OPTION_TO_DB_KEY = {
    OPTION_CLIENT_ID.lower(): "client_id",
    OPTION_CLIENT_SECRET.lower(): "client_secret",
    OPTION_POOL_ADDRESS.lower(): "pool_address",
}
MARKUP = ReplyKeyboardMarkup(REPLY_KEYBOARD, one_time_keyboard=True)


NON_VISIBLE_KEYS = ["channel_id", "_id"]


def _user_data_to_str(user_data: Dict[str, str]) -> str:
    facts = [
        f'➡️{key} - {value}' for key, value in user_data.items() if key not in NON_VISIBLE_KEYS
    ]
    return "\n".join(facts).join(['\n', '\n'])


@only_chat_admin
@only_in_private_chat
def start_setting_channel(update: Update, context: CallbackContext) -> int:
    reply_text = "Please, fill *ALL* items to start using THX API in your channel"
    update.message.reply_text(reply_text, parse_mode='MarkdownV2', reply_markup=MARKUP)

    return CHOOSING


def regular_choice(update: Update, context: CallbackContext) -> int:
    text = update.message.text.lower()
    context.user_data['choice'] = text
    channel = Channel.collection.find_one({'channel_id': context.user_data['channel_id']})
    if channel.get(REPLY_OPTION_TO_DB_KEY[text]):
        reply_text = (
            f"Your {text}? I already know the following about that: "
            f"{channel.get(REPLY_OPTION_TO_DB_KEY[text])}"
        )
    else:
        reply_text = f'Your {text}? Yes, please feel it!'
    update.message.reply_text(reply_text)

    return TYPING_REPLY


def received_information(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    category = context.user_data['choice']
    context.user_data[category] = text.lower()
    del context.user_data['choice']

    channel = Channel.collection.find_one_and_update(
        {'channel_id': context.user_data['channel_id']},
        {'$set': {REPLY_OPTION_TO_DB_KEY[category]: text}},
        # Create new document in case there is none
        upsert=True,
        return_document=ReturnDocument.AFTER
    )
    update.message.reply_text(
        "Cool! Your configuration is:"
        f"{_user_data_to_str(channel)}"
        "You can change client or secret any time.",
        reply_markup=MARKUP,
    )

    return CHOOSING


def done(update: Update, context: CallbackContext) -> int:
    if 'choice' in context.user_data:
        del context.user_data['choice']

    channel = Channel.collection.find_one({'channel_id': context.user_data['channel_id']})
    update.message.reply_text(
        f"Your configuration: {_user_data_to_str(channel)}\nYou can change configuration of your"
        f" channel any time. Just hit /register_channel again!",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END
