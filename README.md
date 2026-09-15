=======
# sculkbot

meme discord bot to detect ref and likns of *Cosmic Princess Kaguya* and notify a selected user(<@780846736922509312> aka sculk1 aka me by default)

## setup

1. create ds bot token
2. enable Message Content Intent the [Discord Developer Portal](https://discord.com/developers/home)
3. create `.env` file in the directory:
```.env
DISCORD_TOKEN=discord_bot_token
CPK_GIF_URL=https://bestsiteever.com/amazingcpk.gif
```
4. iisntall dependencies
```bash
python -m pip install -r requirements.txt
```
5. Start the bot:
```bash
python main.py
```

## commands

commands use "§" prefix, if you dont have it on you keyboard just buy and italian keyboard its 100% worth it
§help lists all avalable commands


## Project Files

- `main.py` idk pretty much everything
- `keywords.py` contains CPK keywords duh
- `.env` stores local secrets, remember to always to `git add .env` :letroll:

## AI Assistance

An AI coding agent was used to provide some support while writing the bot especially but not limited to `keywords.py` and bot logging in `main.py` 
