from telegram import Update
from telegram.ext import CallbackContext

from thx_bot.models.channels import Channel
from thx_bot.models.users import User
from thx_bot.services.thx_api_client import get_member
from thx_bot.validators import only_if_channel_configured
from thx_bot.validators import only_in_private_chat


@only_if_channel_configured
@only_in_private_chat
def get_member_info(update: Update, context: CallbackContext) -> None:
    status, response = get_member(
        User(User.collection.find_one({'user_id': update.effective_user.id,
                                       'channel_id': context.user_data['channel_id']})),
        Channel(Channel.collection.find_one({'channel_id': context.user_data.get('channel_id')}))
    )
    if status != 200:
        update.message.reply_text(
            "This user is not an asset pool member or it is not yet configured"
        )
    else:
        update.message.reply_text(
            f"💲 Your balance is {response['token']['balance']} {response['token']['symbol']}"  # noqa
        )
