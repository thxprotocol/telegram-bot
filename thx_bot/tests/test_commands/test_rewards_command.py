from unittest.mock import MagicMock

import responses
from telegram.constants import CHAT_PRIVATE
from telegram.ext import ConversationHandler

from thx_bot.commands import CHOOSING_REWARDS
from thx_bot.commands import TYPING_REWARD_REPLY
from thx_bot.commands.pool_rewards import done_rewards
from thx_bot.commands.pool_rewards import pool_show_rewards_command
from thx_bot.commands.pool_rewards import received_information_reward
from thx_bot.commands.pool_rewards import regular_choice_reward
from thx_bot.commands.pool_rewards import rewards_entrypoint
from thx_bot.models.channels import Channel
from thx_bot.services.thx_api_client import URL_ASSET_POOL_INFO
from thx_bot.services.thx_api_client import URL_GET_TOKEN
from thx_bot.services.thx_api_client import URL_POOL_REWARDS


def test_start_rewards(with_db, configured_channel, update, context):
    assert rewards_entrypoint(update, context) == CHOOSING_REWARDS


def test_invalid_choice_rewards(with_db, configured_channel, update, context):
    update.message = MagicMock(text="Unknown choice")
    assert regular_choice_reward(update, context) == ConversationHandler.END


def test_valid_choice_reward(with_db, configured_channel, update, context):
    update.message = MagicMock(text="Set Reward")
    assert regular_choice_reward(update, context) == TYPING_REWARD_REPLY


def test_received_invalid_reward_id(with_db, configured_channel, update, context):
    update.message = MagicMock(text="Set Reward")
    regular_choice_reward(update, context)
    info_update = MagicMock(
        effective_chat=MagicMock(type=CHAT_PRIVATE),
        effective_user=MagicMock(id=1),
        message=MagicMock(text="INVALID")
    )
    assert received_information_reward(info_update, context) == CHOOSING_REWARDS
    channel = Channel.collection.find_one({})
    assert channel.get('reward') is None


def test_received_information_reward(with_db, configured_channel, update, context):
    channel = Channel.collection.find_one({})
    assert channel.get('reward') is None
    # Set reward and check if channel was updated with reward
    update.message = MagicMock(text="Set Reward")
    regular_choice_reward(update, context)
    info_update = MagicMock(
        effective_chat=MagicMock(type=CHAT_PRIVATE),
        effective_user=MagicMock(id=1),
        message=MagicMock(text="1")
    )
    assert received_information_reward(info_update, context) == CHOOSING_REWARDS
    channel = Channel.collection.find_one({})
    # Reward ID casted to integer
    assert channel['reward'] == 1


@responses.activate
def test_done_setting_rewards(with_db, configured_channel, update, context):
    responses.add(responses.POST, URL_GET_TOKEN, json={'access_token': 123}, status=200)
    channel = Channel(Channel.collection.find_one({}))
    channel.reward = 1
    channel.save()
    responses.add(responses.GET, f"{URL_POOL_REWARDS}{channel.reward}", json={}, status=200)
    assert done_rewards(update, context) == ConversationHandler.END


@responses.activate
def test_pool_show_rewards_command(with_db, configured_channel, update, context):
    responses.add(responses.POST, URL_GET_TOKEN, json={'access_token': 123}, status=200)
    responses.add(
        responses.GET,
        URL_POOL_REWARDS,
        json=[{'id': 1, 'withdrawAmount': 12}],
        status=200
    )
    responses.add(
        responses.GET,
        f"{URL_ASSET_POOL_INFO}0x123123",
        json={'token': {'symbol': "SOL"}},
        status=200,
    )
    assert pool_show_rewards_command(update, context) == ConversationHandler.END
    update.message.reply_text.assert_called_with('ID: 1 - rewards size: 12 SOL\n')


@responses.activate
def test_pool_show_rewards_command_unhappy(with_db, configured_channel, update, context):
    responses.add(responses.POST, URL_GET_TOKEN, json={'access_token': 123}, status=200)
    responses.add(
        responses.GET,
        URL_POOL_REWARDS,
        json={},
        status=400
    )
    responses.add(
        responses.GET,
        f"{URL_ASSET_POOL_INFO}0x123123",
        json={'token': {'symbol': "SOL"}},
        status=200,
    )
    assert pool_show_rewards_command(update, context) == ConversationHandler.END
    update.message.reply_text.assert_called_with(
        "Your pool is not configured or pool has no rewards"
    )
