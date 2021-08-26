from unittest.mock import MagicMock

import pytest
from telegram.constants import CHATMEMBER_KICKED
from telegram.constants import CHATMEMBER_LEFT
from telegram.constants import CHATMEMBER_MEMBER
from telegram.constants import CHATMEMBER_RESTRICTED
from telegram.constants import CHAT_CHANNEL
from telegram.constants import CHAT_GROUP
from telegram.constants import CHAT_PRIVATE
from telegram.constants import CHAT_SENDER
from telegram.constants import CHAT_SUPERGROUP

from thx_bot.constants import ADMIN_ROLES
from thx_bot.models.channels import Channel
from thx_bot.models.users import User
from thx_bot.validators import only_chat_admin
from thx_bot.validators import only_chat_user
from thx_bot.validators import only_if_channel_configured
from thx_bot.validators import only_in_private_chat
from thx_bot.validators import only_registered_users
from thx_bot.validators import only_unregistered_users


@only_chat_admin
def only_admin_test_function(_, __) -> bool:
    return True


@only_chat_user
def only_member_test_function(_, __) -> bool:
    return True


@only_in_private_chat
def only_private_chat_test_function(_, __) -> bool:
    return True


@only_if_channel_configured
def only_if_channel_configured_test_function(_, __) -> bool:
    return True


@only_unregistered_users
def only_unregistered_users_function(_, __) -> bool:
    return True


@only_registered_users
def only_registered_users_function(_, __) -> bool:
    return True


@pytest.mark.parametrize(
    "member_type",
    [
        *ADMIN_ROLES
    ]
)
def test_only_chat_admin_happy_path(member_type):
    update = MagicMock(effective_chat=MagicMock(type=CHAT_GROUP))
    context = MagicMock(
         bot=MagicMock(get_chat_member=MagicMock(return_value=MagicMock(status=member_type)))
     )
    assert only_admin_test_function(update, context)


@pytest.mark.parametrize(
    "member_type",
    [
        CHATMEMBER_KICKED, CHATMEMBER_LEFT, CHATMEMBER_MEMBER, CHATMEMBER_RESTRICTED
    ]
)
def test_only_chat_admin_unhappy_path(member_type):
    update = MagicMock(effective_chat=MagicMock(type=CHAT_GROUP))
    context = MagicMock(
         bot=MagicMock(get_chat_member=MagicMock(return_value=MagicMock(status=member_type)))
     )
    assert not only_admin_test_function(update, context)


@pytest.mark.parametrize("member_type", [*ADMIN_ROLES, CHATMEMBER_MEMBER])
def test_only_chat_members_happy_path(member_type):
    update = MagicMock(effective_chat=MagicMock(type=CHAT_GROUP))
    context = MagicMock(
         bot=MagicMock(get_chat_member=MagicMock(return_value=MagicMock(status=member_type)))
     )
    assert only_member_test_function(update, context)


@pytest.mark.parametrize("member_type", [CHATMEMBER_RESTRICTED, CHATMEMBER_LEFT, CHATMEMBER_KICKED])
def test_only_chat_members_unhappy_path(member_type):
    update = MagicMock(effective_chat=MagicMock(type=CHAT_GROUP))
    context = MagicMock(
         bot=MagicMock(get_chat_member=MagicMock(return_value=MagicMock(status=member_type)))
     )
    assert not only_member_test_function(update, context)


def test_only_private_chat_happy_path():
    update = MagicMock(effective_chat=MagicMock(type=CHAT_PRIVATE))
    context = MagicMock()
    assert only_private_chat_test_function(update, context)


@pytest.mark.parametrize("chat_type", [CHAT_SENDER, CHAT_GROUP, CHAT_SUPERGROUP, CHAT_CHANNEL])
def test_only_private_chat_unhappy_path(chat_type):
    update = MagicMock(effective_chat=MagicMock(type=chat_type))
    context = MagicMock()
    assert not only_private_chat_test_function(update, context)


def test_only_if_channel_configured_happy_path(with_db):
    update = MagicMock()
    context = MagicMock(user_data={'channel_id': 1})
    channel = Channel(
        client_id=1, channel_id=1, client_secret="somes_secret", pool_address="0x123123123123"
    )
    channel.save()
    assert only_if_channel_configured_test_function(update, context)


def test_only_if_channel_configured_unhappy_path(with_db):
    update = MagicMock()
    context = MagicMock(user_data={'channel_id': 1})
    channel = Channel(
        client_id=1, channel_id=1, client_secret="somes_secret"
    )
    channel.save()
    assert not only_if_channel_configured_test_function(update, context)


@pytest.mark.parametrize(
    "func, expected_output",
    [
        (only_unregistered_users_function, True),
        (only_registered_users_function, None),
    ]
)
def test_unregistered_users(with_db, func, expected_output):
    update = MagicMock(effective_user=MagicMock(id=1))
    context = MagicMock(user_data={'channel_id': 1})
    # User without address is considered unregistered
    user = User(
        user_id=1, email="test@gmail.com", password="qwerty"
    )
    user.save()
    channel = Channel(
        client_id=1, channel_id=1, client_secret="somes_secret", users=[user._id]
    )
    channel.save()
    assert func(update, context) == expected_output


@pytest.mark.parametrize(
    "func, expected_output",
    [
        (only_unregistered_users_function, None),
        (only_registered_users_function, True),
    ]
)
def test_registered_users(with_db, func, expected_output):
    update = MagicMock(effective_user=MagicMock(id=1))
    context = MagicMock(user_data={'channel_id': 1})
    # User without address is considered unregistered
    user = User(
        user_id=1, email="test@gmail.com", password="qwerty", address="0x123123123123123123"
    )
    user.save()
    channel = Channel(
        client_id=1, channel_id=1, client_secret="somes_secret", users=[user._id]
    )
    channel.save()
    assert func(update, context) == expected_output
