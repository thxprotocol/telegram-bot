from unittest.mock import MagicMock

import responses
from telegram.constants import CHAT_PRIVATE
from telegram.ext import ConversationHandler

from thx_bot.commands import CHOOSING_SIGNUP
from thx_bot.commands import TYPING_REPLY_SIGNUP
from thx_bot.commands.create_wallet import done_signup
from thx_bot.commands.create_wallet import received_information_signup
from thx_bot.commands.create_wallet import regular_choice_signup
from thx_bot.commands.create_wallet import start_creating_wallet
from thx_bot.models.channels import Channel
from thx_bot.models.users import User
from thx_bot.services.thx_api_client import URL_GET_TOKEN
from thx_bot.services.thx_api_client import URL_SIGNUP
from thx_bot.utils import fernet


def test_start_signup(with_db, configured_channel, update, context):
    assert start_creating_wallet(update, context) == CHOOSING_SIGNUP


def test_invalid_choice_signup(with_db, configured_channel, update, context):
    update.message = MagicMock(text="Unknown choice")
    assert regular_choice_signup(update, context) == ConversationHandler.END


def test_valid_choice_signup(with_db, configured_channel, update, context):
    update.message = MagicMock(text="Email")
    assert regular_choice_signup(update, context) == TYPING_REPLY_SIGNUP


def test_received_information_signup(with_db, configured_channel, update, context):
    update.message = MagicMock(text="Email")
    regular_choice_signup(update, context)  # To setup choice context
    info_update = MagicMock(
        effective_chat=MagicMock(type=CHAT_PRIVATE),
        effective_user=MagicMock(id=1),
        message=MagicMock(text="a@gmail.com")
    )
    assert received_information_signup(info_update, context) == CHOOSING_SIGNUP
    # User created and filled with info
    user = User.collection.find_one({'email': "a@gmail.com"})
    assert user['user_id'] == update.effective_user.id


def test_received_information_password(with_db, configured_channel, update, context):
    # Check that password was encrypted before DB insertion
    update.message = MagicMock(text="Password")
    regular_choice_signup(update, context)  # To setup choice context
    info_update = MagicMock(
        effective_chat=MagicMock(type=CHAT_PRIVATE),
        effective_user=MagicMock(id=1),
        message=MagicMock(text="qwerty12345")
    )
    assert received_information_signup(info_update, context) == CHOOSING_SIGNUP
    user = User.collection.find_one({})
    assert type(user['password']) == bytes
    assert fernet.decrypt(user['password']).decode() == "qwerty12345"


@responses.activate
def test_done_signup(with_db, configured_channel, update, context):
    responses.add(responses.POST, URL_GET_TOKEN, json={'access_token': 123}, status=200)
    responses.add(responses.POST, URL_SIGNUP, json={'address': "0x123123"}, status=201)
    user = User(
        user_id=1, email="a@gmail.com", password=fernet.encrypt("qwerty".encode()), address=None,
    )
    user.save()
    assert done_signup(update, context) == ConversationHandler.END

    # Make sure user was "attached" to asset pool:
    channel = Channel.collection.find_one({})
    user = User.collection.find_one({})
    assert user['_id'] in channel['users']
    # Make sure user now has address
    assert user['address'] == "0x123123"
    assert user['is_admin']


@responses.activate
def test_done_signup__api_err(with_db, configured_channel, update, context):
    # Pre-create user
    responses.add(responses.POST, URL_GET_TOKEN, json={'access_token': 123}, status=200)
    responses.add(responses.POST, URL_SIGNUP, json={'err': "123"}, status=400)
    user = User(
        user_id=1, email="a@gmail.com", password=fernet.encrypt("qwerty".encode())
    )
    user.save()
    assert done_signup(update, context) == ConversationHandler.END

    user = User.collection.find_one({})
    assert user.get('address') is None
