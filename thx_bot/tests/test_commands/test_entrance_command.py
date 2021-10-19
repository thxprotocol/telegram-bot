from unittest.mock import MagicMock

from telegram.ext import ConversationHandler

from thx_bot.commands import CHOOSING_TOKENS
from thx_bot.commands.entrance import permissions_entrypoint
from thx_bot.commands.entrance import regular_choice_permissions


def test_start_entrance(update, context, configured_channel):
    assert permissions_entrypoint(update, context) == CHOOSING_TOKENS


def test_invalid_choice_rewards(with_db, configured_channel, update, context):
    update.message = MagicMock(text="Unknown choice")
    assert regular_choice_permissions(update, context) == ConversationHandler.END
