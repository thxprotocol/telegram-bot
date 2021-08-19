from thx_bot.models import Model
from thx_bot.models import mongo_client


class Channel(Model):
    collection = mongo_client.thx_tg_integration.asset_pools
