from pymongo import ReturnDocument
from telegram import ReplyKeyboardMarkup
from telegram import ReplyKeyboardRemove
from telegram import Update
from telegram.ext import CallbackContext
from telegram.ext import ConversationHandler

from thx_bot.commands import CHOOSING_REWARDS
from thx_bot.commands import TYPING_REWARD_REPLY
from thx_bot.models.channels import Channel
from thx_bot.services.thx_api_client import get_asset_pool_info
from thx_bot.services.thx_api_client import get_pool_rewards
from thx_bot.validators import only_chat_admin
from thx_bot.validators import only_if_channel_configured
from thx_bot.validators import only_in_private_chat

OPTION_SHOW_REWARDS = "Show rewards"
OPTION_SET_REWARD = "Set Reward"
REPLY_KEYBOARD = [
    [OPTION_SET_REWARD],
    ["Done", OPTION_SHOW_REWARDS],
]
REPLY_OPTION_TO_DB_KEY = {
    OPTION_SET_REWARD.lower(): "reward",
}
MARKUP = ReplyKeyboardMarkup(REPLY_KEYBOARD, one_time_keyboard=True)


@only_if_channel_configured
@only_chat_admin
@only_in_private_chat
def rewards_entrypoint(update: Update, context: CallbackContext) -> int:
    reply_text = "💰 Please, select reward for the channel, " \
                 "so your chat users can start getting rewards"
    update.message.reply_text(reply_text, reply_markup=MARKUP)

    return CHOOSING_REWARDS


@only_if_channel_configured
@only_chat_admin
@only_in_private_chat
def regular_choice_reward(update: Update, context: CallbackContext) -> int:
    text = update.message.text.lower()
    context.user_data['choice'] = text
    channel = Channel.collection.find_one(
        {'channel_id': context.user_data['channel_id']}
    )
    reply_text = "Please, specify reward ID that will be used for you chat:"
    update.message.reply_text(reply_text)

    return TYPING_REWARD_REPLY


@only_chat_admin
@only_in_private_chat
@only_if_channel_configured
def received_information_reward(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    category = context.user_data['choice']
    context.user_data[category] = text.lower()
    del context.user_data['choice']

    channel = Channel.collection.find_one_and_update(
        {'channel_id': context.user_data['channel_id']},
        {'$set': {REPLY_OPTION_TO_DB_KEY[category]: text}},
        return_document=ReturnDocument.AFTER
    )
    update.message.reply_text(
        "Cool! Your reward id for the channel is:"
        f"{channel.get(f'{REPLY_OPTION_TO_DB_KEY[category]}')}",
        reply_markup=MARKUP,
    )

    return CHOOSING_REWARDS


@only_chat_admin
@only_in_private_chat
@only_if_channel_configured
def done_rewards(update: Update, context: CallbackContext) -> int:
    if 'choice' in context.user_data:
        del context.user_data['choice']

    channel = Channel(Channel.collection.find_one({'channel_id': context.user_data['channel_id']}))
    reply = "Please, specify valid reward ID so users can start claiming rewards!"
    if getattr(channel, "reward"):
        status, __ = get_pool_rewards(channel, channel.reward)
        if status == 200:
            reply = f"You have set reward with ID {channel.reward} your channel. " \
                    f"User in your channel now can receive rewards!"
    update.message.reply_text(
        reply,
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END


@only_if_channel_configured
@only_chat_admin
@only_in_private_chat
def pool_rewards_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        "🏆 List of pool rewards:"
    )
    channel = Channel(
        Channel.collection.find_one({'channel_id': context.user_data.get('channel_id')})
    )
    __, rewards_response = get_pool_rewards(channel)
    __, pool_info = get_asset_pool_info(channel)
    rewards = ""
    token = pool_info['token']['symbol']  # noqa
    for reward in rewards_response:
        rewards += f"ID: {reward['id']} - rewards size: {reward['withdrawAmount']} {token}\n"
    update.message.reply_text(rewards)
    return ConversationHandler.END
