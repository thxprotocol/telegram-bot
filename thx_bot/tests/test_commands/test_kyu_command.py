from unittest.mock import MagicMock

import responses
from telegram.constants import CHAT_PRIVATE
from telegram.ext import ConversationHandler

from thx_bot.commands import CHOOSING_KYU
from thx_bot.commands import TYPING_REPLY_KYU
from thx_bot.commands.kyu_command import done_kyu
from thx_bot.commands.kyu_command import received_information_kyu
from thx_bot.commands.kyu_command import regular_choice_kyu
from thx_bot.commands.kyu_command import start_kyu
from thx_bot.models.know_your_user import KnowYourUser
from thx_bot.services.thx_api_client import URL_GET_TOKEN
from thx_bot.services.thx_api_client import URL_POOL_REWARDS
from thx_bot.services.thx_api_client import URL_WITHDRAW


def test_start_kyu(with_db, configured_channel, registered_user, update, context):
    assert start_kyu(update, context) == CHOOSING_KYU


def test_invalid_choice_kyu(with_db, configured_channel, registered_user, update, context):
    update.message = MagicMock(text="Unknown choice")
    assert regular_choice_kyu(update, context) == ConversationHandler.END


def test_valid_choice_kyu(with_db, configured_channel, registered_user, update, context):
    update.message = MagicMock(text="Favourite cryptocurrency 💰")
    assert regular_choice_kyu(update, context) == TYPING_REPLY_KYU


def test_received_information_kyu(with_db, configured_channel, registered_user, update, context):
    update.message = MagicMock(text="Favourite cryptocurrency 💰")
    regular_choice_kyu(update, context)  # To setup choice context
    info_update = MagicMock(
        effective_chat=MagicMock(type=CHAT_PRIVATE),
        effective_user=MagicMock(id=1),
        message=MagicMock(text="SHIB")
    )
    assert received_information_kyu(info_update, context) == CHOOSING_KYU
    # KnowYourUser created and filled with info
    kyu = KnowYourUser.collection.find_one({'fav_crypto': "SHIB"})
    assert kyu['user_id'] == update.effective_user.id
    assert kyu['channel_id'] == context.user_data['channel_id']


@responses.activate
def test_done_kyu_command(
        with_db, configured_channel_with_reward, registered_user, update, context):
    responses.add(responses.POST, URL_GET_TOKEN, json={'access_token': 123}, status=200)
    responses.add(
        responses.POST, f"{URL_POOL_REWARDS}1/give", json={'withdrawal': "1"}, status=200)
    responses.add(
        responses.POST, f"{URL_WITHDRAW}/1/withdraw", json=None, status=200)

    kyu = KnowYourUser(
        user_id=1, channel_id=1,
        fav_crypto="BTT", programming_language="JS", nickname="Jade", crypto_reason="Friends",
    )
    kyu.save()
    done_kyu(update, context)

    kyu_updated = KnowYourUser.collection.find_one({})
    # Make sure user was rewarded
    assert kyu_updated['reward_acquired']

    # Try doing survey again and fail:
    assert not start_kyu(update, context)


def test_done_kyu_command_incomplete_data(
        with_db, configured_channel_with_reward, registered_user, update, context):
    # Incomplete KYU: reward will not be given
    kyu = KnowYourUser(
        user_id=1, channel_id=1,
        fav_crypto="BTT", programming_language="JS", nickname="Jade",
    )
    kyu.save()
    done_kyu(update, context)

    kyu_updated = KnowYourUser.collection.find_one({})
    # Make sure user was rewarded
    assert not kyu_updated.get('reward_acquired')

    # Can start survey again
    assert start_kyu(update, context) == CHOOSING_KYU
