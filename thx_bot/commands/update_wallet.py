from pymongo import ReturnDocument
from telegram import ReplyKeyboardMarkup
from telegram import ReplyKeyboardRemove
from telegram import Update
from telegram.ext import CallbackContext
from telegram.ext import ConversationHandler

from thx_bot.commands import CHOOSING_WALLET_UPDATE
from thx_bot.commands import TYPING_REPLY_WALLET_UPDATE
from thx_bot.commands import user_data_to_str
from thx_bot.models.users import User
from thx_bot.validators import only_chat_user
from thx_bot.validators import only_if_channel_configured
from thx_bot.validators import only_in_private_chat
from thx_bot.validators import only_registered_users

OPTION_WALLET_UPDATE = "Wallet Update"
REPLY_KEYBOARD = [
    [OPTION_WALLET_UPDATE],
    ["Done"],
]
REPLY_OPTION_TO_DB_KEY = {
    OPTION_WALLET_UPDATE.lower(): "address",
}
MARKUP = ReplyKeyboardMarkup(REPLY_KEYBOARD, one_time_keyboard=True)


@only_in_private_chat
@only_if_channel_configured
@only_chat_user
@only_registered_users
def start_updating_wallet(update: Update, context: CallbackContext) -> int:
    reply_text = "💰 Please, paste wallet that you want to use to receive rewards!"
    update.message.reply_text(reply_text, reply_markup=MARKUP)

    return CHOOSING_WALLET_UPDATE


@only_if_channel_configured
@only_in_private_chat
@only_registered_users
@only_chat_user
def regular_choice_wallet_update(update: Update, context: CallbackContext) -> int:
    text = update.message.text.lower()
    if text not in REPLY_OPTION_TO_DB_KEY.keys():
        update.message.reply_text("Unknown choice. Please, click on inline buttons with choices")
        return ConversationHandler.END
    context.user_data['choice'] = text
    user = User.collection.find_one(
        {'user_id': update.effective_user.id, 'channel_id': context.user_data['channel_id']})
    if user and user.get(REPLY_OPTION_TO_DB_KEY[text]):
        reply_text = (
            f"Your {text}? Here is your current wallet: "
            f"{user.get(REPLY_OPTION_TO_DB_KEY[text])}"
            f" Paste here new wallet to change it."
        )
    else:
        reply_text = f'Your {text}? Yes, please fill it!'
    update.message.reply_text(reply_text)

    return TYPING_REPLY_WALLET_UPDATE


@only_if_channel_configured
@only_in_private_chat
@only_registered_users
@only_chat_user
def received_information_wallet_update(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    category = context.user_data['choice']
    context.user_data[category] = text.lower()
    del context.user_data['choice']

    user = User.collection.find_one_and_update(
        {'user_id': update.effective_user.id, 'channel_id': context.user_data['channel_id']},
        {'$set': {'new_address': text}},
        return_document=ReturnDocument.AFTER
    )
    update.message.reply_text(
        "Cool! Your configuration is now:"
        f"{user_data_to_str(user)}\n"
        f"Click DONE when you are ready to submit information.",
        reply_markup=MARKUP,
    )

    return CHOOSING_WALLET_UPDATE


@only_if_channel_configured
@only_in_private_chat
@only_registered_users
@only_chat_user
def done_wallet_update(update: Update, context: CallbackContext) -> int:
    if 'choice' in context.user_data:
        del context.user_data['choice']

    user = User(User.collection.find_one(
        {'user_id': update.effective_user.id, 'channel_id': context.user_data['channel_id']}
    ))
    if not user.new_address:
        update.message.reply_text("Please, set new address!")
        return TYPING_REPLY_WALLET_UPDATE

    user.address = user.new_address
    user.save()

    update.message.reply_text(
        f"Your configuration: {user_data_to_str(user)}\n",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END
