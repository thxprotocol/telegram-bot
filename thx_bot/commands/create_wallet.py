import os

from cryptography.fernet import Fernet
from pymongo import ReturnDocument
from telegram import ReplyKeyboardMarkup
from telegram import ReplyKeyboardRemove
from telegram import Update
from telegram.ext import CallbackContext
from telegram.ext import ConversationHandler

from thx_bot.commands import CHOOSING_SIGNUP
from thx_bot.commands import TYPING_REPLY_SIGNUP
from thx_bot.commands import user_data_to_str
from thx_bot.constants import ADMIN_ROLES
from thx_bot.models.channels import Channel
from thx_bot.models.users import User
from thx_bot.services.thx_api_client import signup_user
from thx_bot.utils import fernet
from thx_bot.validators import only_chat_user
from thx_bot.validators import only_if_channel_configured
from thx_bot.validators import only_in_private_chat
from thx_bot.validators import only_unregistered_users

OPTION_EMAIL = "Email"
OPTION_PASSWORD = "Password"
REPLY_KEYBOARD = [
    [OPTION_EMAIL, OPTION_PASSWORD],
    ["Done"],
]
REPLY_OPTION_TO_DB_KEY = {
    OPTION_EMAIL.lower(): "email",
    OPTION_PASSWORD.lower(): "password",
}
MARKUP = ReplyKeyboardMarkup(REPLY_KEYBOARD, one_time_keyboard=True)


@only_in_private_chat
@only_if_channel_configured
@only_chat_user
@only_unregistered_users
def start_creating_wallet(update: Update, context: CallbackContext) -> int:
    reply_text = "💰 Please, fill both email and password to start getting rewards!"
    update.message.reply_text(reply_text, reply_markup=MARKUP)

    return CHOOSING_SIGNUP


@only_in_private_chat
@only_if_channel_configured
@only_chat_user
@only_unregistered_users
def regular_choice_signup(update: Update, context: CallbackContext) -> int:
    text = update.message.text.lower()
    if text not in REPLY_OPTION_TO_DB_KEY.keys():
        update.message.reply_text("Unknown choice. Please, click on inline buttons with choices")
        return ConversationHandler.END
    context.user_data['choice'] = text
    user = User.collection.find_one({'user_id': update.effective_user.id})
    if user and user.get(REPLY_OPTION_TO_DB_KEY[text]) and not text == OPTION_PASSWORD.lower():
        reply_text = (
            f"Your {text}? I already know the following about that: "
            f"{user.get(REPLY_OPTION_TO_DB_KEY[text])}"
        )
    else:
        reply_text = f'Your {text}? Yes, please fill it!'
    update.message.reply_text(reply_text)

    return TYPING_REPLY_SIGNUP


@only_in_private_chat
@only_if_channel_configured
@only_chat_user
@only_unregistered_users
def received_information_signup(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    category = context.user_data['choice']
    context.user_data[category] = text.lower()
    del context.user_data['choice']

    if REPLY_OPTION_TO_DB_KEY[category] == "password":
        text = fernet.encrypt(text.encode())
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


@only_in_private_chat
@only_if_channel_configured
@only_chat_user
@only_unregistered_users
def done_signup(update: Update, context: CallbackContext) -> int:
    if 'choice' in context.user_data:
        del context.user_data['choice']

    user = User(User.collection.find_one({'user_id': update.effective_user.id}))
    channel = Channel(Channel.collection.find_one_and_update(
        {'channel_id': context.user_data.get('channel_id')},
        {'$addToSet': {'users': user._id}},
        return_document=ReturnDocument.AFTER
    ))
    # Assign this user to admin role if they are chat admin
    chat_member_status = context.bot.get_chat_member(
        int(context.user_data.get('channel_id')), update.effective_user.id).status

    user.is_admin = True if chat_member_status in ADMIN_ROLES else False
    user.save()
    # If API returns !== 201, it means that user was already created in DB or something is wrong
    # with configuration
    status_code, response = signup_user(user, channel)
    if status_code == 201:
        user.address = response['address']
        user.save()
        update.message.reply_text(
            f"Your configuration: {user_data_to_str(user)}\n",
            reply_markup=ReplyKeyboardRemove(),
        )
    else:
        update.message.reply_text(
            "Something went wrong with configuration. Please, try again or try /update_wallet",
            reply_markup=ReplyKeyboardRemove(),
        )
    return ConversationHandler.END
