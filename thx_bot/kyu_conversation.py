from telegram.ext import CommandHandler
from telegram.ext import ConversationHandler
from telegram.ext import Filters
from telegram.ext import MessageHandler

from thx_bot.commands import CHOOSING_KYU
from thx_bot.commands import TYPING_REPLY_KYU
from thx_bot.commands.kyu_command import done_kyu
from thx_bot.commands.kyu_command import received_information_kyu
from thx_bot.commands.kyu_command import regular_choice_kyu
from thx_bot.commands.kyu_command import start_kyu

kyu_conversation = ConversationHandler(
    entry_points=[CommandHandler('introduce', start_kyu)],
    states={  # noqa
        CHOOSING_KYU: [
            MessageHandler(
                Filters.regex(
                    '^(Favourite cryptocurrency 💰|Your programming language 💻|'
                    'Your nickname or other identity 😎|'
                    'What brought you to crypto/blockchains 🏃‍♂️)$'
                ), regular_choice_kyu
            ),
        ],
        TYPING_REPLY_KYU: [
            MessageHandler(
                Filters.text & ~(Filters.command | Filters.regex('^Done ✔️$')),
                received_information_kyu,
            )
        ],
    },
    fallbacks=[MessageHandler(Filters.regex('^Done ✔️$'), done_kyu)],  # noqa
)
