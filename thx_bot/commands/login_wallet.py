from telegram import Update
from telegram.ext import CallbackContext

from thx_bot.models.channels import Channel
from thx_bot.models.users import User
from thx_bot.services.thx_api_client import create_withdraw
from thx_bot.services.thx_api_client import give_reward
from thx_bot.services.thx_api_client import send_login_wallet
from thx_bot.validators import only_if_channel_configured
from thx_bot.validators import only_in_private_chat
from thx_bot.validators import only_registered_users


@only_registered_users
@only_if_channel_configured
@only_in_private_chat
def login_wallet(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        "✉️Please, check you email for THX wallet activation link"
    )
    send_login_wallet(
        User(User.collection.find_one({'user_id': update.effective_user.id})),
        Channel(Channel.collection.find_one({'channel_id': context.user_data.get('channel_id')}))
    )


@only_if_channel_configured
@only_registered_users
@only_in_private_chat
def give_reward_command(update: Update, context: CallbackContext) -> None:
    channel = Channel(
        Channel.collection.find_one({'channel_id': context.user_data.get('channel_id')})
    )
    status, response = give_reward(
        User(User.collection.find_one({'user_id': update.effective_user.id})),
        channel,
    )
    withdrawal = response['withdrawal']
    status, response = create_withdraw(channel=channel, withdrawal=withdrawal)
    update.message.reply_text(
        "HERE IS YOUR REWARD"
    )
