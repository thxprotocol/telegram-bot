from pymongo import ReturnDocument
from telegram import ReplyKeyboardMarkup
from telegram import ReplyKeyboardRemove
from telegram import Update
from telegram.ext import CallbackContext
from telegram.ext import ConversationHandler

from thx_bot.commands import CHOOSING_ADD_MEMBER
from thx_bot.commands import TYPING_REPLY_MEMBER
from thx_bot.commands import user_data_to_str
from thx_bot.models.channels import Channel
from thx_bot.models.users import User
from thx_bot.services.thx_api_client import add_member
from thx_bot.validators import only_chat_user
from thx_bot.validators import only_if_channel_configured
from thx_bot.validators import only_in_private_chat

OPTION_ADD_MEMBER = "Add your wallet"
REPLY_KEYBOARD = [
    [OPTION_ADD_MEMBER],
    ["Done"],
]
REPLY_OPTION_TO_DB_KEY = {
    OPTION_ADD_MEMBER.lower(): "address",
}
MARKUP = ReplyKeyboardMarkup(REPLY_KEYBOARD, one_time_keyboard=True)


@only_in_private_chat
@only_if_channel_configured
def start_adding_member(update: Update, context: CallbackContext) -> int:
    reply_text = "💰 Please, paste wallet that you want to use to receive rewards!" \
                 "Please note, that you have to be registered in THX network already"
    update.message.reply_text(reply_text, reply_markup=MARKUP)

    return CHOOSING_ADD_MEMBER


@only_if_channel_configured
@only_in_private_chat
def regular_choice_member_add(update: Update, context: CallbackContext) -> int:
    text = update.message.text.lower()
    if text not in REPLY_OPTION_TO_DB_KEY.keys():
        update.message.reply_text("Unknown choice. Please, click on inline buttons with choices")
        return ConversationHandler.END

    context.user_data['choice'] = text
    update.message.reply_text("Paste your existing THX wallet and it will be added to members of"
                              "the pool that belongs to the Telegram group")
    return TYPING_REPLY_MEMBER


@only_if_channel_configured
@only_in_private_chat
def received_information_member_add(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    category = context.user_data['choice']
    context.user_data[category] = text.lower()
    del context.user_data['choice']

    user = User(User.collection.find_one_and_update(
        {'user_id': update.effective_user.id, 'channel_id': context.user_data['channel_id']},
        {'$set': {'address': text}},
        upsert=True,
        return_document=ReturnDocument.AFTER,
    ))
    Channel(Channel.collection.find_one_and_update(
        {'channel_id': context.user_data.get('channel_id')},
        {'$addToSet': {'users': user._id}},
        return_document=ReturnDocument.AFTER
    ))
    update.message.reply_text(
        "Cool! Your configuration is now:"
        f"{user_data_to_str(user)}\n"
        f"Click DONE when you are ready to submit information.",
        reply_markup=MARKUP,
    )

    return CHOOSING_ADD_MEMBER


@only_if_channel_configured
@only_in_private_chat
def done_member_add(update: Update, context: CallbackContext) -> int:
    if 'choice' in context.user_data:
        del context.user_data['choice']

    user = User(User.collection.find_one(
        {'user_id': update.effective_user.id, 'channel_id': context.user_data['channel_id']}
    ))
    channel = Channel(
        Channel.collection.find_one({'channel_id': context.user_data.get('channel_id')})
    )
    status, response = add_member(user, channel)
    if status != 200:
        update.message.reply_text(
            "Something is wrong with your address. Make sure you have added correct THX wallet"
            "address and try again!"
        )
    else:
        update.message.reply_text(
            f"Your configuration: {user_data_to_str(user)}\n",
            reply_markup=ReplyKeyboardRemove(),
        )
    return ConversationHandler.END
