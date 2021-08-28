from telegram.ext import CommandHandler
from telegram.ext import ConversationHandler
from telegram.ext import Filters
from telegram.ext import MessageHandler

from thx_bot.commands import CHOOSING
from thx_bot.commands import CHOOSING_REWARDS
from thx_bot.commands import CHOOSING_SIGNUP
from thx_bot.commands import CHOOSING_WALLET_UPDATE
from thx_bot.commands import TYPING_REPLY
from thx_bot.commands import TYPING_REPLY_SIGNUP
from thx_bot.commands import TYPING_REPLY_WALLET_UPDATE
from thx_bot.commands import TYPING_REWARD_REPLY
from thx_bot.commands.create_wallet import done_signup
from thx_bot.commands.create_wallet import received_information_signup
from thx_bot.commands.create_wallet import regular_choice_signup
from thx_bot.commands.create_wallet import start_creating_wallet
from thx_bot.commands.pool_rewards import done_rewards
from thx_bot.commands.pool_rewards import pool_show_rewards_command
from thx_bot.commands.pool_rewards import received_information_reward
from thx_bot.commands.pool_rewards import regular_choice_reward
from thx_bot.commands.pool_rewards import rewards_entrypoint
from thx_bot.commands.register_channel import check_connection_channel
from thx_bot.commands.register_channel import done_channel
from thx_bot.commands.register_channel import received_information_channel
from thx_bot.commands.register_channel import regular_choice_channel
from thx_bot.commands.register_channel import start_setting_channel
from thx_bot.commands.update_wallet import done_wallet_update
from thx_bot.commands.update_wallet import received_information_wallet_update
from thx_bot.commands.update_wallet import regular_choice_wallet_update
from thx_bot.commands.update_wallet import start_updating_wallet

register_channel_conversation = ConversationHandler(
    entry_points=[CommandHandler('register_channel', start_setting_channel)],  # noqa
    states={  # noqa
        CHOOSING: [
            MessageHandler(
                Filters.regex('^(Client id|Client secret|Pool address)$'),
                regular_choice_channel
            ),
        ],
        TYPING_REPLY: [
            MessageHandler(
                Filters.text & ~(Filters.command | Filters.regex('^Done$')),
                received_information_channel,
            )
        ],
    },
    fallbacks=[  # noqa
        MessageHandler(Filters.regex('^Done$'), done_channel),
        MessageHandler(Filters.regex('^Test Connection$'), check_connection_channel),
    ],
    name="register_channel",
    persistent=False,
)


create_wallet_conversation = ConversationHandler(
    entry_points=[CommandHandler('create_wallet', start_creating_wallet)],  # noqa
    states={  # noqa
        CHOOSING_SIGNUP: [
            MessageHandler(
                Filters.regex('^(Email|Password)$'), regular_choice_signup
            ),
        ],
        TYPING_REPLY_SIGNUP: [
            MessageHandler(
                Filters.text & ~(Filters.command | Filters.regex('^Done$')),
                received_information_signup,
            )
        ],
    },
    fallbacks=[  # noqa
        MessageHandler(Filters.regex('^Done$'), done_signup),
    ],  # noqa
    name="create_wallet",
    persistent=False,
)


update_wallet_conversation = ConversationHandler(
    entry_points=[CommandHandler('update_wallet', start_updating_wallet)],  # noqa
    states={  # noqa
        CHOOSING_WALLET_UPDATE: [
            MessageHandler(
                Filters.regex('^Wallet Update$'), regular_choice_wallet_update
            ),
        ],
        TYPING_REPLY_WALLET_UPDATE: [
            MessageHandler(
                Filters.text & ~(Filters.command | Filters.regex('^Done$')),
                received_information_wallet_update,
            )
        ],
    },
    fallbacks=[  # noqa
        MessageHandler(Filters.regex('^Done$'), done_wallet_update),
    ],  # noqa
    name="update_wallet",
    persistent=False,
)


rewards_conversation = ConversationHandler(
    entry_points=[CommandHandler('rewards', rewards_entrypoint)],  # noqa
    states={  # noqa
        CHOOSING_REWARDS: [
            MessageHandler(
                Filters.regex('^Set Reward$'), regular_choice_reward
            ),
        ],
        TYPING_REWARD_REPLY: [
            MessageHandler(
                Filters.text & ~(Filters.command | Filters.regex('^Done$')),
                received_information_reward,
            )
        ],
    },
    fallbacks=[  # noqa
        MessageHandler(Filters.regex('^Done$'), done_rewards),
        MessageHandler(Filters.regex('^Show rewards$'), pool_show_rewards_command),
    ],  # noqa
    name="rewards",
    persistent=False,
)
