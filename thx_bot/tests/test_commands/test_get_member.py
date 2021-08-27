import responses

from thx_bot.commands.get_member import get_member_info
from thx_bot.models.users import User
from thx_bot.services.thx_api_client import MEMBERS_URL
from thx_bot.services.thx_api_client import URL_GET_TOKEN


@responses.activate
def test_get_member(with_db, configured_channel, registered_user, update, context):
    user = User(User.collection.find_one({}))
    responses.add(responses.POST, URL_GET_TOKEN, json={'access_token': 123}, status=200)
    responses.add(
        responses.GET,
        f"{MEMBERS_URL}{user.address}",
        json={'token': {'balance': 12, 'symbol': "TOKX"}},
        status=200)

    assert not get_member_info(update, context)
    update.message.reply_text.assert_called_with(
        "💲 Your balance is 12 TOKX"
    )


@responses.activate
def test_get_member_err(with_db, configured_channel, registered_user, update, context):
    user = User(User.collection.find_one({}))
    responses.add(responses.POST, URL_GET_TOKEN, json={'access_token': 123}, status=200)
    responses.add(
        responses.GET,
        f"{MEMBERS_URL}{user.address}",
        json={},
        status=400)

    assert not get_member_info(update, context)
    update.message.reply_text.assert_called_with(
        "This user is not an asset pool member or it is not yet configured"
    )
