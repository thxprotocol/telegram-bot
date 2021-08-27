from unittest.mock import MagicMock

from telegram.constants import CHAT_PRIVATE
from telegram.ext import ConversationHandler

from thx_bot.commands import CHOOSING_WALLET_UPDATE
from thx_bot.commands import TYPING_REPLY_WALLET_UPDATE
from thx_bot.commands.update_wallet import done_wallet_update
from thx_bot.commands.update_wallet import received_information_wallet_update
from thx_bot.commands.update_wallet import regular_choice_wallet_update
from thx_bot.commands.update_wallet import start_updating_wallet
from thx_bot.models.users import User


def test_start_update_wallet(with_db, registered_user, configured_channel, update, context):
    assert start_updating_wallet(update, context) == CHOOSING_WALLET_UPDATE


def test_invalid_choice_update_wallet(
        with_db, registered_user, configured_channel, update, context):
    update.message = MagicMock(text="Unknown choice")
    assert regular_choice_wallet_update(update, context) == ConversationHandler.END


def test_valid_choice_update_wallet(
        with_db, registered_user, configured_channel, update, context):
    update.message = MagicMock(text="Wallet Update")
    assert regular_choice_wallet_update(update, context) == TYPING_REPLY_WALLET_UPDATE


def test_wallet_updated(
        with_db, registered_user, configured_channel, update, context):
    update.message = MagicMock(text="Wallet Update")
    regular_choice_wallet_update(update, context)

    info_update = MagicMock(
        effective_chat=MagicMock(type=CHAT_PRIVATE),
        effective_user=MagicMock(id=1),
        message=MagicMock(text="0x99999")
    )
    assert received_information_wallet_update(info_update, context) == CHOOSING_WALLET_UPDATE
    # Make sure user address was updated in DB
    user = User.collection.find_one({'new_address': "0x99999"})
    assert user is not None


def test_done_wallet_update(
        with_db, registered_user, configured_channel, update, context):
    user = User.collection.find_one({})

    # First, update user address in DB
    update.message = MagicMock(text="Wallet Update")
    regular_choice_wallet_update(update, context)

    info_update = MagicMock(
        effective_chat=MagicMock(type=CHAT_PRIVATE),
        effective_user=MagicMock(id=1),
        message=MagicMock(text="0x99999")
    )
    received_information_wallet_update(info_update, context)
    assert done_wallet_update(info_update, context) == ConversationHandler.END
    # Make sure user's address is updated
    user = User.collection.find_one({'address': "0x99999"})
    assert user is not None


def test_done_wallet_not_updated(
        with_db, registered_user, configured_channel, update, context):
    # If new_address field is not set before calling this method, it won't call API for update
    assert done_wallet_update(update, context) == TYPING_REPLY_WALLET_UPDATE
