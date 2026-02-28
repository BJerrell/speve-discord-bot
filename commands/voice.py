"""Voice channel commands."""

from discord.ext import commands


async def setup_voice_commands(bot):
    @bot.command(name="join", help="Joins the voice channel you are in.")
    async def join(ctx):
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            await channel.connect()
            await ctx.send(f"Joined {channel.name}!")
        else:
            await ctx.send("You are not connected to a voice channel.")
