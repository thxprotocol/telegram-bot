from time import time

from telegram import Update
from telegram.ext import CallbackContext

from thx_bot.models.channels import Channel
from thx_bot.models.users import User
from thx_bot.services.thx_api_client import get_member
from thx_bot.services.thx_api_client import get_withdrawals_for_member
from thx_bot.validators import only_if_channel_configured_kick_out
from thx_bot.validators import only_if_channel_configured_silent

SECONDS_DELAY = 35


@only_if_channel_configured_silent
@only_if_channel_configured_kick_out
def kick_out_handler(update: Update, context: CallbackContext) -> None:
    for user in update.message.new_chat_members:
        db_user = User.collection.find_one(
            {'user_id': user['id'], 'channel_id': update.effective_chat.id})
        if not db_user:
            context.bot.ban_chat_member(
                update.effective_chat.id, user['id'], until_date=int(time()) + SECONDS_DELAY
            )
            continue
        user_obj = User(db_user)
        channel = Channel(Channel.collection.find_one({'channel_id': update.effective_chat.id}))
        status, response = get_member(user_obj, channel)
        if status != 200:
            context.bot.ban_chat_member(
                update.effective_chat.id, user_obj.id, until_date=int(time()) + SECONDS_DELAY
            )
            continue
        balance = response['token']['balance']  # noqa
        token = response['token']['symbol']  # noqa
        if channel.token and channel.threshold_balance:
            if channel.token != token or balance < channel.threshold_balance:
                context.bot.ban_chat_member(
                    update.effective_chat.id, user_obj.id, until_date=int(time()) + SECONDS_DELAY
                )
                continue
        elif channel.with_reward:
            status, response = get_withdrawals_for_member(user_obj, channel)
            if status != 200:
                context.bot.ban_chat_member(
                    update.effective_chat.id, user_obj.id, until_date=int(time()) + SECONDS_DELAY
                )
                continue
            else:
                if len(response) == 0:
                    context.bot.ban_chat_member(
                        update.effective_chat.id, user_obj.id,
                        until_date=int(time()) + SECONDS_DELAY
                    )
                    continue
