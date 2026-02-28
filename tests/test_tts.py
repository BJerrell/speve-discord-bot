"""Tests for TTS commands."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
import discord
from discord.ext import commands

from commands.tts import setup_tts_commands


class TestSayCommand:

    @pytest.mark.asyncio
    async def test_say_user_not_in_voice(self):
        bot = commands.Bot(command_prefix='!', intents=discord.Intents.default())
        await setup_tts_commands(bot)

        ctx = Mock()
        ctx.send = AsyncMock()
        ctx.author.voice = None

        await bot.get_command('say').callback(ctx, text="hello")

        ctx.send.assert_called_once_with("❌ You need to be in a voice channel.")

    @pytest.mark.asyncio
    async def test_say_already_playing(self):
        bot = commands.Bot(command_prefix='!', intents=discord.Intents.default())
        await setup_tts_commands(bot)

        mock_channel = Mock()
        mock_voice_client = Mock()
        mock_voice_client.channel = mock_channel
        mock_voice_client.is_playing.return_value = True

        ctx = Mock()
        ctx.send = AsyncMock()
        ctx.author.voice = Mock()
        ctx.author.voice.channel = mock_channel
        ctx.voice_client = mock_voice_client

        await bot.get_command('say').callback(ctx, text="hello")

        ctx.send.assert_called_once_with("❌ Already speaking. Wait for the current message to finish.")

    @pytest.mark.asyncio
    async def test_say_connects_and_plays(self):
        bot = commands.Bot(command_prefix='!', intents=discord.Intents.default())
        await setup_tts_commands(bot)

        mock_voice_client = Mock()
        mock_voice_client.is_playing.return_value = False
        mock_voice_client.play = Mock()

        mock_channel = Mock()
        mock_channel.connect = AsyncMock(return_value=mock_voice_client)

        ctx = Mock()
        ctx.send = AsyncMock()
        ctx.author.voice = Mock()
        ctx.author.voice.channel = mock_channel
        ctx.voice_client = None

        with patch('commands.tts._generate_tts', return_value='/tmp/test.mp3'):
            with patch('commands.tts.discord.FFmpegPCMAudio'):
                await bot.get_command('say').callback(ctx, text="hello world")

        mock_channel.connect.assert_called_once()
        mock_voice_client.play.assert_called_once()

    @pytest.mark.asyncio
    async def test_say_moves_to_user_channel(self):
        bot = commands.Bot(command_prefix='!', intents=discord.Intents.default())
        await setup_tts_commands(bot)

        user_channel = Mock()
        bot_channel = Mock()

        mock_voice_client = Mock()
        mock_voice_client.channel = bot_channel
        mock_voice_client.move_to = AsyncMock()
        mock_voice_client.is_playing.return_value = False
        mock_voice_client.play = Mock()

        ctx = Mock()
        ctx.send = AsyncMock()
        ctx.author.voice = Mock()
        ctx.author.voice.channel = user_channel
        ctx.voice_client = mock_voice_client

        with patch('commands.tts._generate_tts', return_value='/tmp/test.mp3'):
            with patch('commands.tts.discord.FFmpegPCMAudio'):
                await bot.get_command('say').callback(ctx, text="hello")

        mock_voice_client.move_to.assert_called_once_with(user_channel)

    @pytest.mark.asyncio
    async def test_say_tts_failure(self):
        bot = commands.Bot(command_prefix='!', intents=discord.Intents.default())
        await setup_tts_commands(bot)

        mock_channel = Mock()
        mock_voice_client = Mock()
        mock_voice_client.channel = mock_channel
        mock_voice_client.is_playing.return_value = False

        ctx = Mock()
        ctx.send = AsyncMock()
        ctx.author.voice = Mock()
        ctx.author.voice.channel = mock_channel
        ctx.voice_client = mock_voice_client

        with patch('commands.tts._generate_tts', side_effect=Exception("network error")):
            await bot.get_command('say').callback(ctx, text="hello")

        ctx.send.assert_called_once_with("❌ Failed to generate speech. Try again later.")


class TestLeaveCommand:

    @pytest.mark.asyncio
    async def test_leave_not_connected(self):
        bot = commands.Bot(command_prefix='!', intents=discord.Intents.default())
        await setup_tts_commands(bot)

        ctx = Mock()
        ctx.send = AsyncMock()
        ctx.voice_client = None

        await bot.get_command('leave').callback(ctx)

        ctx.send.assert_called_once_with("❌ I'm not in a voice channel.")

    @pytest.mark.asyncio
    async def test_leave_connected(self):
        bot = commands.Bot(command_prefix='!', intents=discord.Intents.default())
        await setup_tts_commands(bot)

        mock_voice_client = Mock()
        mock_voice_client.disconnect = AsyncMock()

        ctx = Mock()
        ctx.send = AsyncMock()
        ctx.voice_client = mock_voice_client

        await bot.get_command('leave').callback(ctx)

        mock_voice_client.disconnect.assert_called_once()
        ctx.send.assert_not_called()
