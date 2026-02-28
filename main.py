import os
import logging
import discord
from discord.ext import commands
from dotenv import load_dotenv
from commands.basic import setup_basic_commands
from commands.admin import setup_admin_commands
from commands.voice import setup_voice_commands

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logging.getLogger("discord").setLevel(logging.WARNING)
log = logging.getLogger("speve")


def create_bot():
    intents = discord.Intents.default()
    intents.message_content = True
    prefix = os.getenv("COMMAND_PREFIX", "!")
    bot = commands.Bot(command_prefix=prefix, intents=intents)

    @bot.event
    async def on_ready():
        log.info(f"Logged in as {bot.user} (ID: {bot.user.id})")

    @bot.event
    async def on_command_error(ctx, error):
        if isinstance(error, commands.NotOwner):
            await ctx.send("❌ This command is owner-only.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"❌ Missing argument: `{error.param.name}`")
        elif isinstance(error, commands.CommandNotFound):
            pass
        else:
            log.error(f"Unhandled error in {ctx.command}: {error}", exc_info=error)
            await ctx.send("❌ An unexpected error occurred.")

    async def setup_hook():
        await setup_basic_commands(bot)
        await setup_admin_commands(bot)
        await setup_voice_commands(bot)

    bot.setup_hook = setup_hook
    return bot


def main():
    load_dotenv()
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        print("Error: DISCORD_BOT_TOKEN is not set.")
        print("Create a .env file with DISCORD_BOT_TOKEN=your_token_here")
        raise SystemExit(1)
    bot = create_bot()
    bot.run(token)


if __name__ == "__main__":
    main()
