# Dating-bot
Telegram Dating Bot with Human Match + AI Chat (OpenAI)

# 💖 Dating Bot / GF-BF Bot (Telegram) — Python + MongoDB + OpenAI

A Telegram Dating Bot / GF-BF Bot built with:
- ✅ Python (`python-telegram-bot`)
- ✅ MongoDB Atlas (Database)
- ✅ OpenAI API (AI GF/BF Chat)
- ✅ Koyeb (Deployment as Worker)

This bot supports:
- Registration flow (State → Gender → Age)
- Human matching (Opposite gender preference first → else random)
- AI GF/BF mode (Tamil/English/Hindi/Telugu + style presets)
- Exit + Report system
- Admin panel (broadcast/ban/unban/warn/premium toggle)
- 2 Private group logs:
  - **Group 1**: User start + Registration completed + Reports
  - **Group 2**: Chat logs (for moderation)

---

## 🚀 Deploy on Koyeb (1-Click)

> ✅ Recommended: **Worker Deployment (Polling Bot)**

[![Deploy to Koyeb](https://www.koyeb.com/static/images/deploy/button.svg)](https://app.koyeb.com/deploy?type=git&repository=https://github.com/YOUR_USERNAME/YOUR_REPO&branch=main&name=dating-bot)

📌 **Important:** After clicking deploy, add the environment variables listed below.

---

## ✨ Features

### ✅ Registration
- `/start` → Auto registration starts
- State selection (buttons)
- Gender selection (buttons: Male/Female/Transgender)
- Age input (manual typing)
- Valid age: **18 to 80**

### ✅ Chat Modes
- `/chat` → choose:
  - 👤 Human
  - 🤖 AI

### 🤖 AI GF/BF Chat
- Language select: Tamil/English/Hindi/Telugu
- Style select: Sweet/Romantic/Caring/Possessive/Flirty
- AI replies using **OpenAI API**

### 👤 Human Chat
- Opposite gender matching priority
- Age difference filter
- Partner info shown: state + age + gender
- Buttons:
  - ❌ Exit
  - 🚩 Report

### 🚩 Reporting system
- Sends report to Admin Group1
- Auto disconnect on report

### 🛡️ Moderation
- All human chat messages copied to Group2
- Admin can ban users

---

## 🧑‍💻 Commands

### User Commands
- `/start` — Register
- `/chat` — Choose Human / AI
- `/help`
- `/privacy`
- `/premium`

### Admin Commands (Owner only)
- `/about`
- `/premium_on`
- `/premium_off`
- `/broadcast <message>`
- `/ban <user_id> [reason]`
- `/unban <user_id>`
- `/warn <user_id> <message>`

---

## 🔐 Environment Variables

Create `.env` file in root or set in Koyeb.

### Required
```env
BOT_TOKEN=your_telegram_bot_token
MONGO_URI=mongodb+srv://...
DB_NAME=datingbot

OPENAI_API_KEY=your_openai_key
OPENAI_MODEL=gpt-4o-mini

OWNER_ID=123456789
GROUP1_ID=-100xxxxxxxxxx
GROUP2_ID=-100xxxxxxxxxx
