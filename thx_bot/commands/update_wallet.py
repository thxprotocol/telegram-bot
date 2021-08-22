from telegram import Update
from telegram.ext import CallbackContext

from thx_bot.models.channels import Channel
from thx_bot.models.users import User
from thx_bot.services.thx_api_client import send_login_wallet
from thx_bot.validators import only_if_channel_configured
from thx_bot.validators import only_in_private_chat
from thx_bot.validators import only_registered_users


# @only_registered_users
# @only_if_channel_configured
# @only_in_private_chat
# def login_wallet(update: Update, context: CallbackContext) -> None:
#     update.message.reply_text(
#         "Please, check you email for THX wallet activation link"
#     )
#     update_wallet(
#         User(User.collection.find_one({'user_id': update.effective_user.id})),
#         Channel(Channel.collection.find_one({'channel_id': context.user_data.get('channel_id')}))
#     )
