# THX Telegram Bot "Introduce Yourself" !
## CI and Tests

| CI Status: [![Test](https://github.com/SHAKOTN/thx_tg_bot_contest/actions/workflows/main.yml/badge.svg)](https://github.com/SHAKOTN/thx_tg_bot_contest/actions/workflows/main.yml) | Latest CI runs - [Link](https://github.com/SHAKOTN/thx_tg_bot_contest/actions)|
|---|---:

---

## What this bot is capable of doing?
This bot is built as an integration to [THX Network](https://www.thx.network).

Some of bot's features:
1. Admins of Telegram channels can invite bot to their channel and configure THX integration using `/register_channel` command
2. Admins can set reward for some specific actions users are doing `/rewards`
3. Users of telegram channels(that admins preconfigured) can signup, update their wallets and receive one-time login links to THX wallet app
4. Users of telegram channels can complete Know Your User survey and receive one time rewards by completing it.

## How this bot utilizes gamification of THX Network:
When users enter telegram group they can complete a single "Introduce Yourself` quiz and receive a reward!

## Bot commands
Short description of help info from the bot:
```
🤖     🤖     🤖
Admin Actions:
Connect your channel to work with THX API
/register_channel
Rewards menu, to view and set rewards for your channel
/rewards

If you are channel user:
For signup:
/create_wallet
Send a one-time login link for you wallet(after signup is completed)
Make sure to link your new wallet address with /update_wallet
/login_wallet
Check your wallet balance:
/get_my_info

Tell us about yourself and earn rewards! Once you complete the survey, it will be posted 
the channel and you will receive reward!
/introduce
```

## Security
In this project security was taken as a first priority. 
All bot commands are wrapped into valitador-decorator functions that are checking if user or admin are signed in, if channel is properly configured or if user has given a reward already, so they cannot spam rewards infinitely.

All settings and setups are happening in bot private chat that keeps certain context for the channel that you was redirected from. There is no way you can trick the bot by trying to acquire rewards for the channel that you are not member of.


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
