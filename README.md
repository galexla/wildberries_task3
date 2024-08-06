# Telegram Reminder bot (aiogram)
It can re-post your message after specified time, thus acting as a reminder.

## Start the bot
* `cp template.env .env`
* Set `TG_API_TOKEN` and `TG_BOT_USERNAME` in .env
* Run `python main.py`
* Add this bot to any Telegram chat

## Bot commands
`/start` see welcome message and instructions  
`/ctrl NM` re-post your last message from this chat after NM, where N is a number and M is one of the characters: h, d, w, m (hours, days, weeks, months).