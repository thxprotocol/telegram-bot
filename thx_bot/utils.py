from typing import Union

from thx_bot.models.channels import Channel


def is_channel_configured(chat_id: Union[str, int]) -> bool:
    channel = Channel.collection.find_one({'channel_id': int(chat_id)})
    return all([channel.client_id, channel.client_secret, channel.pool_address])
