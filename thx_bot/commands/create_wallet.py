from pymongo import ReturnDocument
from telegram import ReplyKeyboardMarkup
from telegram import ReplyKeyboardRemove
from telegram import Update
from telegram.ext import CallbackContext
from telegram.ext import ConversationHandler

from thx_bot.commands import CHOOSING_SIGNUP
from thx_bot.commands import TYPING_REPLY_SIGNUP
from thx_bot.commands import user_data_to_str
from thx_bot.models.users import User
from thx_bot.validators import only_chat_user
from thx_bot.validators import only_if_channel_configured
from thx_bot.validators import only_in_private_chat

OPTION_EMAIL = "Email"
OPTION_PASSWORD = "Password"
REPLY_KEYBOARD = [
    [OPTION_EMAIL, OPTION_PASSWORD],
    ['Done'],
]
REPLY_OPTION_TO_DB_KEY = {
    OPTION_EMAIL.lower(): "email",
    OPTION_PASSWORD.lower(): "password",
}
MARKUP = ReplyKeyboardMarkup(REPLY_KEYBOARD, one_time_keyboard=True)


@only_in_private_chat
@only_if_channel_configured
@only_chat_user
def start_creating_wallet(update: Update, context: CallbackContext) -> int:
    reply_text = "💰 Please, fill both email and password to start getting rewards!"
    update.message.reply_text(reply_text, reply_markup=MARKUP)

    return CHOOSING_SIGNUP


def regular_choice_signup(update: Update, context: CallbackContext) -> int:
    text = update.message.text.lower()
    context.user_data['choice'] = text
    user = User.collection.find_one({'user_id': update.effective_user.id})
    if user and user.get(REPLY_OPTION_TO_DB_KEY[text]):
        reply_text = (
            f"Your {text}? I already know the following about that: "
            f"{user.get(REPLY_OPTION_TO_DB_KEY[text])}"
        )
    else:
        reply_text = f'Your {text}? Yes, please feel it!'
    update.message.reply_text(reply_text)

    return TYPING_REPLY_SIGNUP


def received_information_signup(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    category = context.user_data['choice']
    context.user_data[category] = text.lower()
    del context.user_data['choice']

    user = User.collection.find_one_and_update(
        {'user_id': update.effective_user.id},
        {'$set': {REPLY_OPTION_TO_DB_KEY[category]: text}},
        # Create new document in case there is none
        upsert=True,
        return_document=ReturnDocument.AFTER
    )
    update.message.reply_text(
        "Cool! Your configuration is:"
        f"{user_data_to_str(user)}",
        reply_markup=MARKUP,
    )

    return CHOOSING_SIGNUP


def done_signup(update: Update, context: CallbackContext) -> int:
    if 'choice' in context.user_data:
        del context.user_data['choice']

    channel = User.collection.find_one({'user_id': update.effective_user.id})
    update.message.reply_text(
        f"Your configuration: {user_data_to_str(channel)}\n",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END
