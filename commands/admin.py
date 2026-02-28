"""Admin-only Discord bot commands."""

import os
import sys
from discord.ext import commands


async def setup_admin_commands(bot):
    @bot.command(name="restart", help="Restarts the bot. Owner only.")
    @commands.is_owner()
    async def restart(ctx):
        await ctx.send("Restarting...")
        os.execv(sys.executable, [sys.executable] + sys.argv)
