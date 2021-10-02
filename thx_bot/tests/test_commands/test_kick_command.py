import responses

from thx_bot.commands.kick_out import kick_out_handler
from thx_bot.models.users import User
from thx_bot.services.thx_api_client import MEMBERS_URL
from thx_bot.services.thx_api_client import URL_GET_TOKEN


@responses.activate
def test_member_kicked(with_db, configured_channel, registered_user, update, context):
    update.message.new_chat_members = [{'id': 1}]
    user = User(User.collection.find_one({}))
    responses.add(responses.POST, URL_GET_TOKEN, json={'access_token': 123}, status=200)
    responses.add(
        responses.GET,
        f"{MEMBERS_URL}{user.address}",
        json={'token': {'balance': 12, 'symbol': "TOKX"}},
        status=200)

    kick_out_handler(update, context)
    assert context.bot.ban_chat_member.called


@responses.activate
def test_member_kicked__api_err(with_db, configured_channel, registered_user, update, context):
    update.message.new_chat_members = [{'id': 1}]
    user = User(User.collection.find_one({}))
    responses.add(responses.POST, URL_GET_TOKEN, json={'access_token': 123}, status=200)
    responses.add(
        responses.GET,
        f"{MEMBERS_URL}{user.address}",
        json={},
        status=400)

    assert not kick_out_handler(update, context)
    assert context.bot.ban_chat_member.called


@responses.activate
def test_member_not_kicked(with_db, configured_channel, registered_user, update, context):
    update.message.new_chat_members = [{'id': 1}]
    user = User(User.collection.find_one({}))
    responses.add(responses.POST, URL_GET_TOKEN, json={'access_token': 123}, status=200)
    responses.add(
        responses.GET,
        f"{MEMBERS_URL}{user.address}",
        json={'token': {'balance': 100, 'symbol': "THX"}},
        status=200)

    kick_out_handler(update, context)
    assert not context.bot.ban_chat_member.called
