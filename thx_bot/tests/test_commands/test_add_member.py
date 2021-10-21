from unittest.mock import MagicMock

import responses
from telegram.constants import CHAT_PRIVATE
from telegram.ext import ConversationHandler

from thx_bot.commands import CHOOSING_ADD_MEMBER
from thx_bot.commands import TYPING_REPLY_MEMBER
from thx_bot.commands.add_member import done_member_add
from thx_bot.commands.add_member import received_information_member_add
from thx_bot.commands.add_member import regular_choice_member_add
from thx_bot.commands.add_member import start_adding_member
from thx_bot.models.users import User
from thx_bot.services.thx_api_client import MEMBERS_URL
from thx_bot.services.thx_api_client import URL_GET_TOKEN


def test_start_add_member(update, context, configured_channel):
    assert start_adding_member(update, context) == CHOOSING_ADD_MEMBER


def test_invalid_choice_add_member(with_db, configured_channel, update, context):
    update.message = MagicMock(text="Unknown choice")
    assert regular_choice_member_add(update, context) == ConversationHandler.END


def test_valid_choice_add_member(with_db, configured_channel, update, context):
    update.message = MagicMock(text="Add your wallet")
    assert regular_choice_member_add(update, context) == TYPING_REPLY_MEMBER


def test_received_valid_add_member(with_db, configured_channel, update, context):
    assert not User.collection.find_one({})
    info_update = MagicMock(
        effective_chat=MagicMock(type=CHAT_PRIVATE),
        effective_user=MagicMock(id=1),
        message=MagicMock(text="0x5A36206D7cC1c4F498819260b44E64DC245fDbdB")
    )

    update.message = MagicMock(text="Add your wallet")
    regular_choice_member_add(update, context)

    received_information_member_add(info_update, context)

    # Make sure user document gets created
    user = User.collection.find_one({})
    assert user['address'] == "0x5A36206D7cC1c4F498819260b44E64DC245fDbdB"


@responses.activate
def test_done_add_member(with_db, configured_channel, update, context):
    responses.add(responses.POST, URL_GET_TOKEN, json={'access_token': 123}, status=200)
    responses.add(
        responses.POST,
        MEMBERS_URL,
        json={},
        status=200,
    )
    info_update = MagicMock(
        effective_chat=MagicMock(type=CHAT_PRIVATE),
        effective_user=MagicMock(id=1),
        message=MagicMock(text="0x5A36206D7cC1c4F498819260b44E64DC245fDbdB")
    )

    update.message = MagicMock(text="Add your wallet")
    regular_choice_member_add(update, context)

    received_information_member_add(info_update, context)
    assert done_member_add(update, context) == ConversationHandler.END
    assert "Your configuration is now:" in str(info_update.message.reply_text.call_args_list)
