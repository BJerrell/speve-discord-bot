"""Text-to-speech commands for voice channels."""

import asyncio
import os
import tempfile

import discord
from discord.ext import commands
from gtts import gTTS


def _generate_tts(text: str, language: str, slow: bool) -> str:
    """Generate a TTS audio file and return its path."""
    tts = gTTS(text=text, lang=language, slow=slow)
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        tts.save(f.name)
        return f.name


async def setup_tts_commands(bot):

    @bot.command(name="say", help="Speaks text in your voice channel.")
    async def say(ctx, *, text: str):
        if not ctx.author.voice:
            await ctx.send("❌ You need to be in a voice channel.")
            return

        channel = ctx.author.voice.channel

        if ctx.voice_client is None:
            voice_client = await channel.connect()
        elif ctx.voice_client.channel != channel:
            await ctx.voice_client.move_to(channel)
            voice_client = ctx.voice_client
        else:
            voice_client = ctx.voice_client

        if voice_client.is_playing():
            await ctx.send("❌ Already speaking. Wait for the current message to finish.")
            return

        language = os.getenv("TTS_LANGUAGE", "en")
        slow = os.getenv("TTS_SLOW", "false").lower() == "true"

        try:
            loop = asyncio.get_running_loop()
            temp_path = await loop.run_in_executor(None, _generate_tts, text, language, slow)
        except Exception:
            await ctx.send("❌ Failed to generate speech. Try again later.")
            return

        def after_playing(error):
            try:
                os.unlink(temp_path)
            except OSError:
                pass

        voice_client.play(discord.FFmpegPCMAudio(temp_path), after=after_playing)

    @bot.command(name="leave", help="Leaves the voice channel.")
    async def leave(ctx):
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
        else:
            await ctx.send("❌ I'm not in a voice channel.")
