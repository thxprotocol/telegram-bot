# Know Your User command

from pymongo import ReturnDocument
from telegram import ReplyKeyboardMarkup
from telegram import ReplyKeyboardRemove
from telegram import Update
from telegram.ext import CallbackContext
from telegram.ext import ConversationHandler

from thx_bot.commands import CHOOSING_KYU
from thx_bot.commands import TYPING_REPLY_KYU
from thx_bot.commands import user_data_to_str
from thx_bot.models.channels import Channel
from thx_bot.models.know_your_user import KnowYourUser
from thx_bot.models.users import User
from thx_bot.services.thx_api_client import create_withdraw
from thx_bot.services.thx_api_client import give_reward
from thx_bot.utils import filled_all_facts
from thx_bot.validators import only_if_channel_configured
from thx_bot.validators import only_in_private_chat
from thx_bot.validators import only_registered_users
from thx_bot.validators import only_users_without_reward

FAV_CRYPTO = "Favourite cryptocurrency 💰"
PROGRAMMING_LANGUAGE = "Your programming language 💻"
CRYPTO_REASON = "What brought you to crypto/blockchains 🏃‍♂️"
OTHER_NICKNAME = "Your nickname or other identity 😎"

REPLY_KEYBOARD = [
    [FAV_CRYPTO, PROGRAMMING_LANGUAGE],
    [CRYPTO_REASON, OTHER_NICKNAME],
    ["Done ✔️"],
]

REPLY_OPTION_TO_HUMAN_READABLE_VALUE = {
    FAV_CRYPTO: "your favorite cryptocurrency(token/coin)",
    PROGRAMMING_LANGUAGE: "your language that you use to code",
    CRYPTO_REASON: "reason that brought you to crypto",
    OTHER_NICKNAME: "your nickname or identity that we can use to call you in the chat",
}

REPLY_OPTION_TO_DB_KEY = {
    FAV_CRYPTO.lower(): "fav_crypto",
    PROGRAMMING_LANGUAGE.lower(): "programming_language",
    CRYPTO_REASON.lower(): "crypto_reason",
    OTHER_NICKNAME.lower(): "nickname",
}


MARKUP = ReplyKeyboardMarkup(REPLY_KEYBOARD, one_time_keyboard=True)


@only_if_channel_configured
@only_in_private_chat
@only_registered_users
@only_users_without_reward
def start_kyu(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        "Hi! I am telegram bot that will ask certain questions about yourself 🤖\n"
        " Once you complete survey and hit DONE button, you will receive a reward!",
        reply_markup=MARKUP,
    )

    return CHOOSING_KYU


@only_if_channel_configured
@only_in_private_chat
@only_registered_users
@only_users_without_reward
def regular_choice_kyu(update: Update, context: CallbackContext) -> int:
    text = update.message.text.lower()
    if text not in REPLY_OPTION_TO_DB_KEY.keys():
        update.message.reply_text("Unknown choice. Please, click on inline buttons with choices")
        return ConversationHandler.END
    text = update.message.text
    context.user_data['choice'] = text
    update.message.reply_text(f"Please, tell me your {REPLY_OPTION_TO_HUMAN_READABLE_VALUE[text]}!")

    return TYPING_REPLY_KYU


@only_if_channel_configured
@only_in_private_chat
@only_registered_users
@only_users_without_reward
def received_information_kyu(update: Update, context: CallbackContext) -> int:
    user_data = context.user_data
    text = update.message.text
    category = REPLY_OPTION_TO_DB_KEY[user_data['choice'].lower()]
    user_data[category] = text
    del user_data['choice']

    know_your_user = KnowYourUser.collection.find_one_and_update(
        {'user_id': update.effective_user.id,
         'channel_id': context.user_data.get('channel_id')},
        {'$set': {category: text}},
        # Create new document in case there is none
        upsert=True, return_document=ReturnDocument.AFTER
    )
    update.message.reply_text(
        "This is what you already told me:"
        f"{user_data_to_str(know_your_user)} You can tell me more, or change your opinion"
        " on something.",
        reply_markup=MARKUP,
    )

    return CHOOSING_KYU


@only_if_channel_configured
@only_in_private_chat
@only_registered_users
@only_users_without_reward
def done_kyu(update: Update, context: CallbackContext) -> int:
    user_data = context.user_data
    if 'choice' in user_data:
        del user_data['choice']

    know_your_user = KnowYourUser.collection.find_one(
        {'user_id': update.effective_user.id,
         'channel_id': context.user_data.get('channel_id')},
    )

    update.message.reply_text(
        f"I learned these facts about you: {user_data_to_str(know_your_user)}"
        f"If you filled all facts - you will receive a reward! Please, check your wallet info "
        f"with /get_my_info command.",
        reply_markup=ReplyKeyboardRemove(),
    )
    know_your_user_obj = KnowYourUser(know_your_user)
    if filled_all_facts(know_your_user_obj):
        channel = Channel(
            Channel.collection.find_one({'channel_id': context.user_data.get('channel_id')})
        )
        user = User(User.collection.find_one({'user_id': update.effective_user.id}))
        status, response = give_reward(user, channel)
        if status != 200:
            update.message.reply_text("Failed to give reward")
            return ConversationHandler.END
        withdrawal = response['withdrawal']
        withdraw_status = create_withdraw(channel=channel, withdrawal=withdrawal)
        if withdraw_status != 200:
            update.message.reply_text("Failed to give reward")
        else:
            update.message.reply_text("You acquired reward!")
            know_your_user_obj.reward_acquired = True
            know_your_user_obj.save()
            context.bot.send_message(
                context.user_data['channel_id'],
                "Hey chat! This is THX Bot speaking."
                f"Please, welcome: {update.effective_user.name}! \n"
                f"Here are some facts about them: {user_data_to_str(know_your_user)}"
            )

    return ConversationHandler.END
