from telegram import Update
from telegram.ext import CallbackContext

from thx_bot.models.channels import Channel
from thx_bot.services.thx_api_client import get_pool_rewards
from thx_bot.validators import only_if_channel_configured
from thx_bot.validators import only_in_private_chat
from thx_bot.validators import only_registered_users


@only_if_channel_configured
@only_registered_users
@only_in_private_chat
def pool_rewards_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        "🏆 List of pool rewards:"
    )
    __, rewards_response = get_pool_rewards(
        Channel(Channel.collection.find_one({'channel_id': context.user_data.get('channel_id')}))
    )
    rewards = ""
    for reward in rewards_response:
        rewards += f"ID: {reward['id']} - rewards size: {reward['withdrawAmount']}\n"
    update.message.reply_text(rewards)
