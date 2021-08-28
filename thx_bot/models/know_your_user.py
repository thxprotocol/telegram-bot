from thx_bot.models import Model
from thx_bot.models import mongo_client


class KnowYourUser(Model):
    """
    Model to keep users answers about themselves tied to specific channel
    """
    collection = mongo_client.thx_tg_integration.know_your_users
