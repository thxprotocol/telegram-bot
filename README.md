# THX Telegram bot integration for Gitcoin Hackathon
## CI and Tests

| CI Status: [![Test](https://github.com/SHAKOTN/thx_tg_bot_contest/actions/workflows/main.yml/badge.svg)](https://github.com/SHAKOTN/thx_tg_bot_contest/actions/workflows/main.yml) | Latest CI runs - [Link](https://github.com/SHAKOTN/thx_tg_bot_contest/actions)|
|---|---:

---

## What this bot is capable of doing?
This bot is built as an integration to [THX Network](https://www.thx.network).

Some of bot's features:
1. Admins of Telegram channels can invite bot to their channel and configure THX integration using `/register_channel` command
2. Admins can set reward for some specific actions users are doing `/rewards`
3. Users of telegram channels(that admins preconfigured) can signup, update their wallet and acquire rewards by doing channel-specific tasks


## Setting things up
To run this bot locally:
1. Talk to [Botfather](https://t.me/botfather) and register your new bot. After everything is done, Botfather will give you bot token
2. Create .env file in project root and fill following ENV variables: `BOT_TOKEN` with token that you received from Botfather during step1; `MONGODB_USERNAME`, `MONGODB_PASSWORD` and `MONGODB_HOSTNAME`; `SECRET_KEY` that can be generated using `cryptography.Fernet`. Example of .env file:
```BOT_TOKEN=<BOT_TOKEN>
MONGODB_DATABASE=thx_integration
MONGODB_USERNAME=root
MONGODB_PASSWORD=my_pwd
MONGODB_HOSTNAME=mongodb
SECRET_KEY=<SECRET_KEY>
```
3. Run `docker-compose build`
4. Run `docker-compose up`

You are all set!