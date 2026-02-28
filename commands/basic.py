"""Basic Discord bot commands."""

from discord.ext import commands


async def setup_basic_commands(bot):
    @bot.command(name="hello")
    async def hello(ctx):
        await ctx.send(f"Hello, {ctx.author.mention}! 👋")

    @bot.command(name="ping")
    async def ping(ctx):
        await ctx.send("Pong! 🏓")

    @bot.command(name="🏓", help="Pong")
    async def pong(ctx):
        await ctx.send("🏓")

    @bot.command(name="echo", help="Repeats the user's message.")
    async def echo(ctx, *, message: str):
        await ctx.send(message)
