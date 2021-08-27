from unittest.mock import MagicMock

from thx_bot.utils import is_channel_configured
from thx_bot.utils import is_user_signed_up


def test_channel_configured():
    assert is_channel_configured(
        MagicMock(client_id=123, client_secret="secret", pool_address="0x123")
    )


def test_channel_not_configured():
    assert not is_channel_configured(
        MagicMock(client_id=123, client_secret="secret", pool_address=None))
    assert not is_channel_configured(
        MagicMock(client_id=123, pool_address="0x123", client_secret=None))


def test_user_registered():
    assert is_user_signed_up(MagicMock(email="2@gmail.com", password="123", address="0x123"))


def test_user_unregistered():
    assert not is_user_signed_up(
        MagicMock(email="2@gmail.com", password="secret", address=None))
    assert not is_user_signed_up(
        MagicMock(email="2@gmail.com", password=None, address="0x123"))
