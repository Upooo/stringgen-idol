# 🤖 STRIDOLBot

> **Telegram String Session Generator for the IDOL Ecosystem**

**STRIDOLBot** is a lightweight Telegram utility bot built for the **IDOL ecosystem**.

Its primary purpose is simple:

**Generate a Telegram String Session securely based on the framework selected by the user.**

Currently supported frameworks:

* **Telethon**
* **Pyrogram v2**

The project is intentionally focused on session generation in V1, without unnecessary infrastructure or features.

---

## ✨ Features

### Session Generation

* Choose between **Telethon** and **Pyrogram v2**
* Phone number authentication
* OTP verification
* 2FA password support
* Generate and return a String Session
* Security warning after successful generation

### Session Management

* In-memory per-user state
* Automatic state timeout
* One active generation process per user
* `/cancel` command
* Cancel button
* Automatic cleanup after:

  * Successful generation
  * Cancellation
  * Authentication error
  * Timeout
  * Unexpected failure

### 🔐 Security

STRIDOLBot is designed to minimize the exposure and lifetime of sensitive authentication data.

* Session strings are **never permanently stored**
* OTP codes are **never logged**
* 2FA passwords are **never logged**
* API hashes are **never logged**
* Bot tokens are **never logged**
* Temporary authentication state exists **only in memory**
* Temporary state is automatically cleaned up
* Users receive a clear security warning after session generation

> ⚠️ **Never share your String Session with anyone.**
>
> A String Session can provide access to your Telegram account. Treat it like a password or private key.

---

## 🧩 Supported Frameworks

| Framework   |        Status        |
| ----------- | :------------------: |
| Telethon    |        ✅ Ready       |
| Pyrogram v2 |        ✅ Ready       |
| GramJS      | ⏳ Not planned for V1 |
| Others      |       ⏳ Future       |

---

## 🎯 V1 Scope

STRIDOLBot V1 intentionally focuses on one responsibility:

> **Telegram String Session Generation**

The following features are **not included in V1**:

* ❌ GramJS
* ❌ Database
* ❌ PostgreSQL
* ❌ Redis
* ❌ Celery / background workers
* ❌ Docker orchestration
* ❌ Payment system
* ❌ Subscription / billing
* ❌ User management
* ❌ Admin dashboard
* ❌ Deployment system
* ❌ Userbot hosting
* ❌ Userbot monitoring
* ❌ REST API
* ❌ Web dashboard
* ❌ AI features

Keeping V1 small makes the system easier to maintain, audit, and extend later.

---

## 🏗️ Architecture

```text
                    ┌─────────────────────┐
                    │    Telegram User   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Telegram Bot      │
                    │     aiogram 3       │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │     Handlers &       │
                    │     Keyboards        │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Session Service    │
                    │   In-Memory State    │
                    └──────────┬──────────┘
                               │
                    ┌──────────┴──────────┐
                    ▼                     ▼
          ┌──────────────────┐   ┌──────────────────┐
          │ Telethon         │   │ Pyrogram v2      │
          │ Session Generator│   │ Session Generator│
          └──────────────────┘   └──────────────────┘
```

### Core Components

**Bot Layer**

* Telegram interaction
* Commands
* Callback buttons
* User input handling

**Session Service**

* Authentication flow
* Per-user session state
* Timeout handling
* Cleanup

**Framework Generators**

* Telethon session generation
* Pyrogram v2 session generation

---

## 📁 Project Structure

```text
stringgen-idol/
│
├── src/
│   ├── main.py
│   ├── config.py
│   │
│   ├── bot/
│   │   ├── handlers/
│   │   │   ├── start.py
│   │   │   └── session.py
│   │   │
│   │   └── keyboards/
│   │       └── session.py
│   │
│   ├── generators/
│   │   ├── base.py
│   │   ├── telethon.py
│   │   └── pyrogram.py
│   │
│   └── services/
│       ├── state.py
│       └── session_service.py
│
├── tests/
│
├── .env.example
├── .gitignore
├── pyproject.toml
└── README.md
```

---

## 🚀 Installation

### Requirements

* **Python 3.10+**
* Telegram Bot Token
* Telegram API ID
* Telegram API Hash

### 1. Clone the Repository

```bash
git clone https://github.com/Upooo/stringgen-idol.git
cd stringgen-idol
```

### 2. Create Virtual Environment

```bash
python3.10 -m venv .venv
```

Activate it:

**Linux / macOS**

```bash
source .venv/bin/activate
```

**Windows**

```powershell
.venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -e ".[dev]"
```

---

## ⚙️ Configuration

Create your environment file:

```bash
cp .env.example .env
```

Then configure:

```env
BOT_TOKEN=your_bot_token

ENVIRONMENT=development
LOG_LEVEL=INFO

TELETHON_API_ID=12345
TELETHON_API_HASH=your_telethon_api_hash

PYROGRAM_API_ID=12345
PYROGRAM_API_HASH=your_pyrogram_api_hash
```

Get your Telegram API credentials from:

**https://my.telegram.org**

> 🔒 **Never commit `.env` or real credentials to Git.**

---

## ▶️ Running

Start the bot with:

```bash
python -m src.main
```

Then open your Telegram bot and send:

```text
/start
```

---

## 🧪 Testing

Run the test suite:

```bash
pytest
```

---

## 🔄 User Flow

The authentication flow is intentionally straightforward:

```text
/start
   │
   ▼
Generate String Session
   │
   ▼
Choose Framework
   ├── Telethon
   └── Pyrogram v2
   │
   ▼
Enter Phone Number
   │
   ▼
Enter OTP
   │
   ├── 2FA Enabled ──► Enter 2FA Password
   │
   ▼
Generate Session String
   │
   ▼
Return Session + Security Warning
   │
   ▼
Optional Message Deletion
```

---

## 🛡️ Security Model

STRIDOLBot follows a **no-persistent-session-storage** approach.

Sensitive authentication information is processed temporarily during the generation flow and removed when the process finishes.

```text
User
 │
 │ Phone / OTP / 2FA
 ▼
Bot
 │
 ▼
Temporary In-Memory State
 │
 ▼
Framework Generator
 │
 ▼
Session String
 │
 ▼
User
 │
 ▼
Cleanup
```

No database is required for the V1 architecture.

---

## 📊 V1 Development Status

| Phase | Description           | Status |
| ----: | --------------------- | :----: |
|    01 | Foundation            | ✅ Done |
|    02 | Session State Manager | ✅ Done |
|    03 | Telethon Generator    | ✅ Done |
|    04 | Pyrogram v2 Generator | ✅ Done |
|    05 | Security Review       | ✅ Done |
|    06 | Final Testing         | ✅ Done |

### Current Status

**V1 — Complete ✅**

The core String Session generation workflow is implemented for both supported frameworks.

---

## 🧭 Future Direction

Future versions may expand STRIDOLBot beyond basic session generation.

Potential areas include:

* Additional Telegram frameworks
* Persistent user management
* Admin controls
* Session management
* Usage analytics
* Web dashboard
* REST API
* Subscription system
* Payment integration
* Deployment automation
* Userbot infrastructure
* Monitoring
* AI-assisted features

These features are intentionally outside the scope of V1.

---

## ⚠️ Disclaimer

STRIDOLBot is provided as a utility for legitimate Telegram development and automation workflows.

Users are responsible for how they use generated sessions and must protect their authentication credentials.

**Never share your String Session, OTP, 2FA password, API credentials, or Bot Token with untrusted parties.**

---

## 📜 License

License information will be added in a future release.
