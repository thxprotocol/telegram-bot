from unittest.mock import MagicMock

import pytest
from telegram.constants import CHATMEMBER_CREATOR
from telegram.constants import CHAT_PRIVATE

from thx_bot.models import mongo_client
from thx_bot.models.channels import Channel
from thx_bot.models.users import User


def purge_database() -> None:
    User.collection = mongo_client.test_db.users
    Channel.collection = mongo_client.test_db.channels
    for model in [User, Channel]:
        model.collection.remove({})


@pytest.fixture
def with_db():
    purge_database()
    yield
    purge_database()


@pytest.fixture
def context():
    return MagicMock(
        user_data={'channel_id': 1},
        bot=MagicMock(get_chat_member=MagicMock(return_value=MagicMock(status=CHATMEMBER_CREATOR)))
    )


@pytest.fixture
def update():
    return MagicMock(
        effective_chat=MagicMock(type=CHAT_PRIVATE),
        effective_user=MagicMock(id=1),
    )


@pytest.fixture
def configured_channel():
    channel = Channel(
        client_id=1, channel_id=1, client_secret="somes_secret", pool_address="0x123123",
    )
    channel.save()


@pytest.fixture
def registered_user(configured_channel):
    user = User(
        email="a@gmail.com", password=b"qwerty12345", address="0x123123123", user_id=1,
    )
    user.save()
    channel = Channel(Channel.collection.find_one({}))
    channel.users = [user._id]
    channel.save()
