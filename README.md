# Speve Discord Bot

A Discord bot built with Python and discord.py.

## Features

- **Basic Commands**: Hello, ping, echo
- **Voice Support**: Join voice channels
- **Admin Commands**: Restart (owner only)
- **Configurable**: via `.env` file

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure

Create a `.env` file in the project root (get your token from the [Discord Developer Portal](https://discord.com/developers/applications)):

```
DISCORD_BOT_TOKEN=your_token_here
```

`COMMAND_PREFIX` defaults to `!` and can be omitted unless you want to change it.

### 3. Run

```bash
python main.py
```

The bot will print a confirmation once it connects:
```
Logged in as YourBot#1234 (ID: 123456789)
```

## Commands

| Command | Description |
|---|---|
| `!hello` | Greet the bot |
| `!ping` | Check bot responsiveness |
| `!🏓` | Responds with 🏓 |
| `!echo <message>` | Bot repeats your message |
| `!join` | Bot joins your voice channel |
| `!restart` | Restart the bot (owner only) |

## Project Structure

```
DiscordBot/
├── main.py              # Entry point
├── commands/
│   ├── basic.py         # hello, ping, echo, 🏓
│   ├── admin.py         # restart
│   └── voice.py         # join
├── tests/
├── .env                 # Your secrets (gitignored)
├── .env.example         # Template
├── requirements.txt
└── requirements-test.txt
```

## Running Tests

```bash
pip install -r requirements-test.txt
pytest tests/
```

## Configuration

| Variable | Default | Description |
|---|---|---|
| `DISCORD_BOT_TOKEN` | *(required)* | Your Discord bot token |
| `COMMAND_PREFIX` | `!` | Prefix for bot commands |
