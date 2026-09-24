# GOD ITACHI FILE HOST BOT

## Environment variables
- `BOT_TOKEN` = your new BotFather token
- `ADMIN_ID` = your numeric Telegram user ID

Do not put the bot token inside `bot.py` or commit it to GitHub.

## Start
```bash
pip install -r requirements.txt
python bot.py
```

## Important
This bot stores SQLite data and uploaded files on local disk. On free hosting, local disk may not be persistent across restarts/redeploys. For reliable file hosting, use persistent external storage.
