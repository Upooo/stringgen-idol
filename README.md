# STRIDOLBot

**STRIDOLBot** is a Telegram utility bot from the IDOL ecosystem focused on one primary function:

> Generate a Telegram String Session for the user based on the framework they choose.

## Supported Frameworks (V1)

| Framework     | Status  |
|---------------|---------|
| Telethon      | ✅ Ready |
| Pyrogram v2   | ✅ Ready |

**Not included in V1:**
- GramJS
- Database / PostgreSQL / Redis
- Celery / workers
- Docker orchestration
- Payment / subscription / billing
- User management / admin dashboard
- Deployment system
- Userbot hosting / monitoring
- REST API / web dashboard
- AI features

## Features

- Choose Telethon or Pyrogram v2
- Phone number login → OTP → 2FA (if enabled)
- Generate and return session string
- In-memory per-user state with timeout
- `/cancel` command + Cancel button
- One active generation process per user
- Automatic cleanup after success / cancel / error / timeout
- Clear security warning after session is generated

## Architecture

Telegram Bot (aiogram 3) │ ▼ Handlers + Keyboards │ ▼ Session Service (in-memory state) │ ▼ Framework Generators ├── TelethonSessionGenerator └── PyrogramSessionGenerator

text

## Project Structure

stringgen-idol/ ├── src/ │   ├── main.py │   ├── config.py │   ├── bot/ │   │   ├── handlers/ │   │   │   ├── start.py │   │   │   └── session.py │   │   └── keyboards/ │   │       └── session.py │   ├── generators/ │   │   ├── base.py │   │   ├── telethon.py │   │   └── pyrogram.py │   └── services/ │       ├── state.py │       └── session_service.py ├── tests/ ├── .env.example ├── .gitignore ├── pyproject.toml └── README.md

text

## Installation

Requires **Python 3.10+**.

```bash
git clone https://github.com/Upooo/stringgen-idol.git
cd stringgen-idol
python3.10 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

Configuration

Bash

cp .env.example .env

Fill in .env:

env

BOT_TOKEN=your_bot_token

ENVIRONMENT=development
LOG_LEVEL=INFO

TELETHON_API_ID=12345
TELETHON_API_HASH=your_telethon_api_hash

PYROGRAM_API_ID=12345
PYROGRAM_API_HASH=your_pyrogram_api_hash





Get API ID / Hash from https://my.telegram.org



Never commit .env or real credentials

Running

Bash

python -m src.main

Send /start to your bot.

Testing

Bash

pytest

Security





Session strings, OTP, 2FA passwords, API hashes, and bot token are never logged



No permanent storage of sessions



Temporary state is in-memory only, keyed by Telegram user ID



Automatic cleanup on success, cancel, error, and timeout



Users receive a clear security warning after generation

User Flow





/start



Tap Generate String Session



Choose Telethon or Pyrogram v2



Send phone number (+62...)



Enter OTP



Enter 2FA password (if enabled)



Receive session string + security warning



Optionally delete the message

V1 Scope Status

PhaseDescriptionStatus1Foundation✅ Done2Session state manager✅ Done3Telethon generator✅ Done4Pyrogram v2 generator✅ Done5Security review✅ Done6Final testing✅ Done

