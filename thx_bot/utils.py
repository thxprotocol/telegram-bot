import os

from cryptography.fernet import Fernet

from thx_bot.models.channels import Channel
from thx_bot.models.know_your_user import KnowYourUser
from thx_bot.models.users import User


def is_channel_configured(chat: Channel) -> bool:
    if not chat:
        return False
    return all([chat.client_id, chat.client_secret, chat.pool_address])


def is_user_signed_up(user: User) -> bool:
    if not user:
        return False
    return all([user.email, user.password, user.address]) or user.address


def filled_all_facts(know_your_user: KnowYourUser):
    return all([
        know_your_user.fav_crypto, know_your_user.programming_language,
        know_your_user.nickname, know_your_user.crypto_reason,
    ])


fernet = Fernet(os.getenv("SECRET_KEY").encode())
