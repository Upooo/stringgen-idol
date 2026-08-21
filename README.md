# STRIDOLBot

**STRIDOLBot** is a Telegram utility bot from the IDOL ecosystem focused on one primary function:

> Generate a Telegram String Session for the user based on the framework they choose.

## Supported Frameworks (V1)

| Framework     | Status            |
|---------------|-------------------|
| Telethon      | Planned (Phase 3) |
| Pyrogram v2   | Planned (Phase 4) |

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

## Architecture (high level)
Telegram Bot (aiogram 3)
│
▼
Handlers + Keyboards
│
▼
Session Service (in-memory state)
│
▼
Framework Generators
├── TelethonSessionGenerator
└── PyrogramSessionGenerator
text- **Async-first** using `aiogram` 3.x, Telethon, and Pyrogram 2.x.
- Configuration via `pydantic-settings` and environment variables.
- Per-user in-memory state with timeout and cleanup (Phase 2+).
- Strict security rules around credentials, OTP, 2FA, and session strings.

## Project Structure
stringgen-idol/
├── src/
│   ├── init.py
│   ├── main.py
│   ├── config.py
│   ├── bot/
│   │   ├── handlers/
│   │   │   ├── start.py
│   │   │   └── session.py
│   │   └── keyboards/
│   │       └── session.py
│   ├── generators/
│   │   ├── base.py
│   │   ├── telethon.py
│   │   └── pyrogram.py
│   └── services/
│       └── session_service.py
├── tests/
│   ├── test_config.py
│   └── test_generators.py
├── .env.example
├── .gitignore
├── pyproject.toml
└── README.md
text## Installation

Requires **Python 3.10+**.

```bash
git clone https://github.com/Upooo/stringgen-idol.git
cd stringgen-idol
python3.10 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
Configuration
Bashcp .env.example .env
Fill in:
envBOT_TOKEN=
ENVIRONMENT=development
LOG_LEVEL=INFO
TELETHON_API_ID=
TELETHON_API_HASH=
PYROGRAM_API_ID=
PYROGRAM_API_HASH=

Never commit .env or any real credentials.
API ID / Hash from https://my.telegram.org

Running Locally
Bashpython -m src.main
Testing
Bashpytest
Security Considerations

Never log session strings, OTP, 2FA passwords, API hashes, or bot tokens.
Never store session strings permanently.
Temporary state is in-memory, keyed by Telegram user ID, with timeout + cleanup.
State isolation between users.
Clear security warning after session generation.

Current V1 Scope








































PhaseDescriptionStatus1Foundation✅ Done2Session state managerPending3Telethon generatorPending4Pyrogram v2 generatorPending5Security reviewPending6Final testingPending
Future Possibilities (out of V1 scope)

GramJS support
Persistent storage (if needed)
Rate limiting improvements
Multi-language UI
Deployment helpers
