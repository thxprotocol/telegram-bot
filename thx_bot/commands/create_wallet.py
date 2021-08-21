from pymongo import ReturnDocument
from telegram import ReplyKeyboardMarkup
from telegram import ReplyKeyboardRemove
from telegram import Update
from telegram.ext import CallbackContext
from telegram.ext import ConversationHandler

from thx_bot.commands import CHOOSING_SIGNUP
from thx_bot.commands import TYPING_REPLY_SIGNUP
from thx_bot.commands import user_data_to_str
from thx_bot.models.channels import Channel
from thx_bot.models.users import User
from thx_bot.services.thx_api_client import signup_user
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

    user = User(User.collection.find_one({'user_id': update.effective_user.id}))
    if not context.user_data.get('channel_id'):
        update.message.reply_text("⛔ Oops. Something is wrong with chat configuration. "
                                  "Please, contact your chat admin")
    channel = Channel(Channel.collection.find_one_and_update(
        {'channel_id': context.user_data.get('channel_id')},
        {'$addToSet': {'users': user._id}},
        return_document=ReturnDocument.AFTER
    ))
    # If API returns !== 200, it means that user was already created in DB or something is wrong
    # with configuration
    status_code, response = signup_user(user, channel)
    if status_code == 200:
        user.address = response['address']
        user.save()

    update.message.reply_text(
        f"Your configuration: {user_data_to_str(user)}\n",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END

# TODO: Get user checks
# def check_signup(update: Update, context: CallbackContext) -> int:
#     channel = Channel.collection.find_one(
#         {'channel_id': context.user_data.get('channel_id')}
#     )
#     # Check that user was added to channel, so they can use chat secret to query API
#     user = User.collection.find_one(
#         {'user_id': update.effective_user.id, '_id': {'$in': channel.get('users')}},
#     )
#     if is_channel_configured(channel):
#         pass
#     return ConversationHandler.END
