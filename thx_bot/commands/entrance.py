from pymongo import ReturnDocument
from telegram import ReplyKeyboardMarkup
from telegram import Update
from telegram.ext import CallbackContext
from telegram.ext import ConversationHandler
from thx_bot.commands import CHOOSING_TOKENS
from thx_bot.commands import TYPING_TOKENS_REPLY
from thx_bot.models.channels import Channel
from thx_bot.services.thx_api_client import get_asset_pool_info
from thx_bot.validators import only_chat_admin
from thx_bot.validators import only_if_channel_configured
from thx_bot.validators import only_in_private_chat


OPTION_SET_MINIMUM_TOKENS = "Set entrance amount"
OPTION_SHOW_CONFIGURATION = "Show entrance configuration"
OPTION_DISABLE_ENTRANCE_CHECKS = "Disable entrance checks"
OPTION_ENABLE_USERS_WITH_REWARDS = "Toggle only users with rewards"


REPLY_KEYBOARD = [
    [OPTION_SET_MINIMUM_TOKENS],
    ["Done", OPTION_SHOW_CONFIGURATION, OPTION_ENABLE_USERS_WITH_REWARDS,
     OPTION_DISABLE_ENTRANCE_CHECKS],
]

REPLY_OPTION_TO_DB_KEY = {
    OPTION_SET_MINIMUM_TOKENS.lower(): "threshold_balance",
}

MARKUP = ReplyKeyboardMarkup(REPLY_KEYBOARD, one_time_keyboard=True)


@only_chat_admin
@only_if_channel_configured
@only_in_private_chat
def permissions_entrypoint(update: Update, context: CallbackContext):
    reply_text = "💰 Please, select amount of tokens that is minimum to enter your chat. Please" \
                 "note that token type will be taken from your THX configured pool"
    update.message.reply_text(reply_text, reply_markup=MARKUP)

    return CHOOSING_TOKENS


@only_if_channel_configured
@only_chat_admin
@only_in_private_chat
def regular_choice_permissions(update: Update, context: CallbackContext):
    text = update.message.text.lower()
    if text not in REPLY_OPTION_TO_DB_KEY.keys():
        update.message.reply_text("Unknown choice. Please, click on inline buttons with choices")
        return ConversationHandler.END
    text = update.message.text.lower()
    context.user_data['choice'] = text
    reply_text = "Please, specify amount of tokens that is minimum to enter the chat"
    update.message.reply_text(reply_text)

    return TYPING_TOKENS_REPLY


@only_chat_admin
@only_in_private_chat
@only_if_channel_configured
def received_permission_amount(update: Update, context: CallbackContext):
    try:
        text = int(update.message.text)
    except ValueError:
        update.message.reply_text(
            "Please, specify valid amount of tokens",
            reply_markup=MARKUP,
        )
        return CHOOSING_TOKENS
    category = context.user_data['choice']
    context.user_data[category] = text
    del context.user_data['choice']
    channel = Channel(Channel.collection.find_one_and_update(
        {'channel_id': context.user_data['channel_id']},
        {'$set': {REPLY_OPTION_TO_DB_KEY[category]: text}},
        return_document=ReturnDocument.AFTER
    ))
    pool_status, pool_info = get_asset_pool_info(channel)
    if pool_status != 200:
        update.message.reply_text(
            "Your pool is not configured. Please, make sure to configure it "
            "in THX app: https://dashboard.thx.network/"
        )
        return ConversationHandler.END
    token = pool_info['token']['symbol']  # noqa
    channel.token = token
    channel.save()
    update.message.reply_text(
        f"Cool! Amount of tokens to enter your group is: {channel.threshold_balance}",
        reply_markup=MARKUP,
    )
    return CHOOSING_TOKENS


@only_chat_admin
@only_in_private_chat
@only_if_channel_configured
def done_permission(update: Update, context: CallbackContext):
    if 'choice' in context.user_data:
        del context.user_data['choice']

    channel = Channel(Channel.collection.find_one({'channel_id': context.user_data['channel_id']}))
    if getattr(channel, "token") and getattr(channel, "threshold_balance"):
        update.message.reply_text(
            f"You successfully configured your channel "
            f"to have minimum entrance amount of tokens as:"
            f" {channel.threshold_balance} {channel.token}")
    else:
        update.message.reply_text("Channel is not configured yet. Please, "
                                  "check your THX configuration")
    return ConversationHandler.END


@only_chat_admin
@only_in_private_chat
@only_if_channel_configured
def show_entrance_permision_for_channel(update: Update, context: CallbackContext):
    channel = Channel(
        Channel.collection.find_one({'channel_id': context.user_data.get('channel_id')})
    )
    if getattr(channel, "token") and getattr(channel, "threshold_balance"):
        update.message.reply_text(
            f"💰 Your channel has minimum amount of tokens required: "
            f"{channel.threshold_balance} {channel.token}"
        )
    else:
        update.message.reply_text(
            "You haven't configured minimum amount of tokens required for entrance of chat yet"
        )
    return ConversationHandler.END


@only_chat_admin
@only_in_private_chat
@only_if_channel_configured
def disable_entrance_checks(update: Update, context: CallbackContext):
    channel = Channel(
        Channel.collection.find_one({'channel_id': context.user_data.get('channel_id')})
    )
    if getattr(channel, "token") and getattr(channel, "threshold_balance"):
        update.message.reply_text(
            f"Channel no longer has any entrance checks"
        )
        channel.token = None
        channel.threshold_balance = None
        channel.save()
    return ConversationHandler.END


@only_chat_admin
@only_in_private_chat
@only_if_channel_configured
def toggle_users_with_rewards(update: Update, context: CallbackContext):
    channel = Channel(
        Channel.collection.find_one({'channel_id': context.user_data.get('channel_id')})
    )
    if any(
        [channel.token, channel.threshold_balance]
    ):
        update.message.reply_text(
            "You already have enabled entrance by token amount. These different entrance conditions"
            "are mutually exclusive. If you want to use entrance by reward, first disable "
            "entrance by token"
        )
        return 
    channel.with_reward = not channel.with_reward
    toggled = "switched on" if channel.with_reward else "switched off"
    update.message.reply_text(
        f"Channel now has {toggled} entrance with rewards only feature"
    )
    channel.save()
    return ConversationHandler.END
