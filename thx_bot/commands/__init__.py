from typing import Dict

CHOOSING, TYPING_REPLY = range(2)
CHOOSING_REWARDS, TYPING_REWARD_REPLY = range(7, 9)
CHOOSING_SIGNUP, TYPING_REPLY_SIGNUP = range(3, 5)
CHOOSING_WALLET_UPDATE, TYPING_REPLY_WALLET_UPDATE = range(5, 7)
CHOOSING_KYU, TYPING_REPLY_KYU = range(10, 12)
CHOOSING_TOKENS, TYPING_TOKENS_REPLY = range(13, 15)
CHOOSING_ADD_MEMBER, TYPING_REPLY_MEMBER = range(16, 18)


NON_VISIBLE_KEYS = ["channel_id", "user_id", "_id", "users", "password", "reward_acquired"]


def user_data_to_str(user_data: Dict[str, str]) -> str:
    if user_data:
        facts = [
            f'➡️{key} - {value}' for key, value in user_data.items()
            if key not in NON_VISIBLE_KEYS
        ]
        return "\n".join(facts).join(['\n', '\n'])
