from unittest.mock import MagicMock

import responses
from telegram.constants import CHAT_PRIVATE
from telegram.ext import ConversationHandler

from thx_bot.commands import CHOOSING_TOKENS
from thx_bot.commands import TYPING_TOKENS_REPLY
from thx_bot.commands.entrance import done_permission
from thx_bot.commands.entrance import permissions_entrypoint
from thx_bot.commands.entrance import received_permission_amount
from thx_bot.commands.entrance import regular_choice_permissions
from thx_bot.models.channels import Channel
from thx_bot.services.thx_api_client import URL_ASSET_POOL_INFO
from thx_bot.services.thx_api_client import URL_GET_TOKEN


def test_start_entrance(update, context, configured_channel):
    assert permissions_entrypoint(update, context) == CHOOSING_TOKENS


def test_invalid_choice_entrance(with_db, configured_channel, update, context):
    update.message = MagicMock(text="Unknown choice")
    assert regular_choice_permissions(update, context) == ConversationHandler.END


def test_valid_choice_entrance(with_db, configured_channel, update, context):
    update.message = MagicMock(text="Set entrance amount")
    assert regular_choice_permissions(update, context) == TYPING_TOKENS_REPLY


def test_received_invalid_amount_entrance(with_db, configured_channel, update, context):
    info_update = MagicMock(
        effective_chat=MagicMock(type=CHAT_PRIVATE),
        effective_user=MagicMock(id=1),
        message=MagicMock(text="INVALID")
    )
    assert received_permission_amount(info_update, context) == CHOOSING_TOKENS
    assert info_update.message.reply_text.called
    assert "Please, specify valid amount of tokens" \
           in str(info_update.message.reply_text.call_args_list)


@responses.activate
def test_received_valid_amount_entrance(with_db, configured_channel, update, context):
    responses.add(responses.POST, URL_GET_TOKEN, json={'access_token': 123}, status=200)
    responses.add(
        responses.GET,
        f"{URL_ASSET_POOL_INFO}0x123123",
        json={'token': {'symbol': "SOL"}},
        status=200,
    )
    info_update = MagicMock(
        effective_chat=MagicMock(type=CHAT_PRIVATE),
        effective_user=MagicMock(id=1),
        message=MagicMock(text="100")
    )

    update.message = MagicMock(text="Set entrance amount")
    regular_choice_permissions(update, context)

    received_permission_amount(info_update, context)

    # Make sure channel document gets updated
    channel = Channel.collection.find_one({})
    assert channel['token'] == "SOL"
    assert channel['threshold_balance'] == 100


@responses.activate
def test_done_entrance_configuration(with_db, configured_channel, update, context):
    responses.add(responses.POST, URL_GET_TOKEN, json={'access_token': 123}, status=200)
    responses.add(
        responses.GET,
        f"{URL_ASSET_POOL_INFO}0x123123",
        json={'token': {'symbol': "SOL"}},
        status=200,
    )
    info_update = MagicMock(
        effective_chat=MagicMock(type=CHAT_PRIVATE),
        effective_user=MagicMock(id=1),
        message=MagicMock(text="100")
    )

    update.message = MagicMock(text="Set entrance amount")
    regular_choice_permissions(update, context)

    received_permission_amount(info_update, context)
    assert done_permission(update, context) == ConversationHandler.END
    assert "Cool! Amount of tokens to enter your group is: 100" \
           in str(info_update.message.reply_text.call_args_list)
