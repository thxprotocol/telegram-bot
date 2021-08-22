
from thx_bot.models.channels import Channel
from thx_bot.models.users import User


def is_channel_configured(chat: Channel) -> bool:
    if not chat:
        return False
    return all([chat.client_id, chat.client_secret, chat.pool_address])


def is_user_signed_up(user: User) -> bool:
    if not user:
        return False
    return all([user.email, user.password, user.address])
