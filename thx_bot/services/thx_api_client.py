from base64 import b64encode
from typing import Dict
from typing import List
from typing import Tuple

import requests

from thx_bot.models.channels import Channel
from thx_bot.models.users import User
from thx_bot.utils import fernet

URL_GET_TOKEN = "https://api.thx.network/token"
URL_ASSET_POOL_INFO = "https://api.thx.network/v1/asset_pools/"
URL_POOL_REWARDS = "https://api.thx.network/v1/rewards"
URL_SIGNUP = "https://api.thx.network/v1/signup"
MEMBERS_URL = "https://api.thx.network/v1/members/"
ACTIVATION_URL = "https://api.thx.network/v1/authentication_token"


def get_token_auth_headers(client_id: str, client_secret: str) -> dict:
    auth_header_encoded = b64encode(f"{client_id}:{client_secret}".encode()).decode('utf-8')
    return {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': f"Basic {auth_header_encoded}"
    }


def get_api_token(channel: Channel) -> Tuple[int, Dict[str, str]]:
    response = requests.post(
        URL_GET_TOKEN,
        data={
            'grant_type': "client_credentials",
            'scope': "openid admin",
        },
        headers=get_token_auth_headers(channel.client_id, channel.client_secret)
    )
    return response.status_code, response.json()


def get_asset_pool_info(channel: Channel) -> Tuple[int, Dict[str, str]]:
    # TODO: Handle case when there is error
    __, token_response = get_api_token(channel)
    token = token_response['access_token']
    response = requests.get(
        f"{URL_ASSET_POOL_INFO}{channel.pool_address}",
        headers={
            'Content-Type': "application/json",
            'Authorization': f"Bearer {token}",
        }
    )
    return response.status_code, response.json()


def get_pool_rewards(channel: Channel) -> Tuple[int, List[Dict[str, str]]]:
    __, token_response = get_api_token(channel)
    token = token_response['access_token']
    response = requests.get(
        f"{URL_POOL_REWARDS}",
        headers={
            'Content-Type': "application/json",
            'AssetPool': channel.pool_address,
            'Authorization': f"Bearer {token}",
        }
    )
    return response.status_code, response.json()


def signup_user(user: User, channel: Channel) -> Tuple[int, Dict[str, str]]:
    password = fernet.decrypt(user.password).decode()
    __, token_response = get_api_token(channel)
    token = token_response['access_token']
    response = requests.post(
        URL_SIGNUP,
        data={
            'email': user.email,
            'password': password,
            'confirmPassword': password,
        },
        headers={
            'AssetPool': channel.pool_address,
            'Authorization': f"Bearer {token}",
        },
    )
    return response.status_code, response.json()


def get_member(user: User, channel: Channel) -> Tuple[int, Dict[str, str]]:
    __, token_response = get_api_token(channel)
    token = token_response['access_token']
    response = requests.get(
        f"{MEMBERS_URL}{user.address}",
        headers={
            'AssetPool': channel.pool_address,
            'Authorization': f"Bearer {token}",
        }
    )
    return response.status_code, response.json()


def send_login_wallet(user: User, channel: Channel) -> Tuple[int, Dict[str, str]]:
    password = fernet.decrypt(user.password).decode()
    __, token_response = get_api_token(channel)
    token = token_response['access_token']
    response = requests.post(
        ACTIVATION_URL,
        data={
            'email': user.email,
            'password': password,
        },
        headers={
            'Authorization': f"Bearer {token}",
        },
    )
    return response.status_code, response.json()


def send_update_wallet(user: User, channel: Channel) -> Tuple[int, Dict[str, str]]:
    __, token_response = get_api_token(channel)
    token = token_response['access_token']
    response = requests.patch(
        f"{MEMBERS_URL}{user.address}",
        data={
            'address': user.new_address,
            'isManager': False,
        },
        headers={
            'AssetPool': channel.pool_address,
            'Authorization': f"Bearer {token}",
        },
    )
    return response.status_code, response.json()
