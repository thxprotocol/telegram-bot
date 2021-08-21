from thx_bot.models.channels import Channel


def is_channel_configured(chat: Channel) -> bool:
    return all([chat.client_id, chat.client_secret, chat.pool_address])
