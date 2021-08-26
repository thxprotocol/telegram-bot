from unittest.mock import MagicMock

import responses
from telegram.constants import CHAT_PRIVATE
from telegram.ext import ConversationHandler

from thx_bot.commands import CHOOSING
from thx_bot.commands import TYPING_REPLY
from thx_bot.commands.register_channel import CONNECTION_FAILED
from thx_bot.commands.register_channel import CONNECTION_SUCCESSFUL
from thx_bot.commands.register_channel import check_connection_channel
from thx_bot.commands.register_channel import done_channel
from thx_bot.commands.register_channel import received_information_channel
from thx_bot.commands.register_channel import regular_choice_channel
from thx_bot.commands.register_channel import start_setting_channel
from thx_bot.models.channels import Channel
from thx_bot.services.thx_api_client import URL_ASSET_POOL_INFO
from thx_bot.services.thx_api_client import URL_GET_TOKEN


def test_start_setting_channel(update, context):
    assert start_setting_channel(update, context) == CHOOSING


def test_upsert_channel_on_setting_choice(with_db, update, context):
    assert Channel.collection.find_one({}) is None
    update.message = MagicMock(text="Pool address")
    assert regular_choice_channel(update, context) == TYPING_REPLY

    channel = Channel.collection.find_one({})
    assert channel['channel_id'] == 1


def test_upsert_channel_on_setting_choice_unknown_choice(with_db, update, context):
    update.message = MagicMock(text="Unknown choice")
    assert regular_choice_channel(update, context) == ConversationHandler.END
    assert Channel.collection.find_one({}) is None


def test_info_received(with_db, update, context):
    update.message = MagicMock(text="Pool address")
    # To create channel
    regular_choice_channel(update, context)
    info_update = MagicMock(
        effective_chat=MagicMock(type=CHAT_PRIVATE),
        effective_user=MagicMock(id=1),
        message=MagicMock(text="0x123123123123")
    )
    assert received_information_channel(info_update, context) == CHOOSING
    # Make sure channel is updated with correct pool address:
    channel = Channel.collection.find_one({})
    assert channel['pool_address'] == "0x123123123123"


def test_done_channel(update, context):
    assert done_channel(update, context) == ConversationHandler.END


@responses.activate
def test_check_connection_channel(with_db, update, context):
    address = "0x123123"
    responses.add(responses.POST, URL_GET_TOKEN, json={'access_token': 123}, status=200)
    responses.add(responses.GET, f"{URL_ASSET_POOL_INFO}{address}", json={}, status=200)
    channel = Channel(
        client_id=1, channel_id=1, client_secret="somes_secret", pool_address=address,
    )
    channel.save()
    assert check_connection_channel(update, context) == ConversationHandler.END
    update.message.reply_text.assert_called_with(CONNECTION_SUCCESSFUL)


@responses.activate
def test_check_connection_channel_api_returns_err(with_db, update, context):
    address = "0x123123"
    responses.add(responses.POST, URL_GET_TOKEN, json={'access_token': 123}, status=200)
    responses.add(responses.GET, f"{URL_ASSET_POOL_INFO}{address}", json={}, status=400)
    channel = Channel(
        client_id=1, channel_id=1, client_secret="somes_secret", pool_address=address,
    )
    channel.save()
    assert check_connection_channel(update, context) == ConversationHandler.END
    update.message.reply_text.assert_called_with(CONNECTION_FAILED)
