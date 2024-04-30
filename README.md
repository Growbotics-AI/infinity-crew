# Infinity Crew Telegram Bot

## Overview
This repository hosts the Telegram bot for the Infinity Crew, part of the One-Person Unicorn Experiment documented at [Solo Unicorn](https://solounicorn.substack.com/). This bot leverages the Llama 3 70B model to autonomously manage tasks via Telegram.

## Quick Start

### Prerequisites
- Python 3.8+
- Telegram account
- Necessary API keys (OpenAI, Telegram)

### Environment Variables
Set the following environment variables before running the bot:
- `TELEGRAM_BOT_TOKEN='your_telegram_bot_token'`
- `TELEGRAM_USER_ID='your_telegram_user_id'`
- `TELEGRAM_WEBHOOK_URL='your_webhook_url'`
- `OLLAMA_API_BASE='your_ollama_api_base_url'`

### Installation and Usage
1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-repository/infinity-crew-bot.git
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure environment variables as described above.**
4. **Run the bot:**
   ```bash
   python main.py
   ```
5. **Interact with the bot on Telegram using `/crew` to assign tasks.**

## License
MIT License

## More Information
For a detailed journey through the project, visit [Solo Unicorn](https://solounicorn.substack.com/).
