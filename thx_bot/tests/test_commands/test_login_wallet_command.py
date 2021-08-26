import os

import responses
from cryptography.fernet import Fernet

from thx_bot.commands.login_wallet import login_wallet
from thx_bot.models.channels import Channel
from thx_bot.models.users import User
from thx_bot.services.thx_api_client import ACTIVATION_URL
from thx_bot.services.thx_api_client import URL_GET_TOKEN


@responses.activate
def test_login_wallet_called(with_db, update, context):
    address = "0x123123"
    responses.add(responses.POST, URL_GET_TOKEN, json={'access_token': 123}, status=200)
    responses.add(responses.POST, ACTIVATION_URL, json={}, status=200)
    fernet = Fernet(os.getenv("SECRET_KEY").encode())
    password = fernet.encrypt("qwerty".encode())
    user = User(
        user_id=1, email="test@gmail.com", password=password, address="0x123123123123123123"
    )
    user.save()
    channel = Channel(
        client_id=1, channel_id=1, client_secret="somes_secret",
        pool_address=address, users=[user._id]
    )
    channel.save()

    assert not login_wallet(update, context)
    update.message.reply_text.assert_called_with(
        "✉️Please, check you email for THX wallet activation link")
