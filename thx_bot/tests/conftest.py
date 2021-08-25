import pytest

from thx_bot.models.channels import Channel
from thx_bot.models.users import User


def purge_database() -> None:
    for model in [User, Channel]:
        model.collection.remove({})


@pytest.fixture
def with_db():
    purge_database()
    yield
    purge_database()
