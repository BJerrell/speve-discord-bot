"""Tests for bot commands."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
import discord
from discord.ext import commands

from commands.basic import setup_basic_commands
from commands.admin import setup_admin_commands
from commands.voice import setup_voice_commands
from commands.tts import setup_tts_commands


class TestBasicCommands:
    """Test basic bot commands."""

    @pytest.mark.asyncio
    async def test_setup_basic_commands(self):
        mock_bot = Mock()
        mock_bot.command = Mock()

        await setup_basic_commands(mock_bot)

        assert mock_bot.command.call_count == 4  # hello, ping, 🏓, echo
        command_names = [c[1].get('name') for c in mock_bot.command.call_args_list]
        assert 'hello' in command_names
        assert 'ping' in command_names
        assert '🏓' in command_names
        assert 'echo' in command_names

    @pytest.mark.asyncio
    async def test_hello_command(self):
        bot = commands.Bot(command_prefix='!', intents=discord.Intents.default())
        await setup_basic_commands(bot)

        ctx = Mock()
        ctx.author.mention = "<@123456789>"
        ctx.send = AsyncMock()

        await bot.get_command('hello').callback(ctx)

        ctx.send.assert_called_once()
        response = ctx.send.call_args[0][0]
        assert "Hello" in response
        assert "<@123456789>" in response
        assert "👋" in response

    @pytest.mark.asyncio
    async def test_ping_command(self):
        bot = commands.Bot(command_prefix='!', intents=discord.Intents.default())
        await setup_basic_commands(bot)

        ctx = Mock()
        ctx.send = AsyncMock()

        await bot.get_command('ping').callback(ctx)

        ctx.send.assert_called_once_with("Pong! 🏓")

    @pytest.mark.asyncio
    async def test_pong_command(self):
        bot = commands.Bot(command_prefix='!', intents=discord.Intents.default())
        await setup_basic_commands(bot)

        ctx = Mock()
        ctx.send = AsyncMock()

        await bot.get_command('🏓').callback(ctx)

        ctx.send.assert_called_once_with("🏓")

    @pytest.mark.asyncio
    async def test_echo_command(self):
        bot = commands.Bot(command_prefix='!', intents=discord.Intents.default())
        await setup_basic_commands(bot)

        ctx = Mock()
        ctx.send = AsyncMock()

        await bot.get_command('echo').callback(ctx, message="hello there")

        ctx.send.assert_called_once_with("hello there")


class TestAdminCommands:
    """Test admin bot commands."""

    @pytest.mark.asyncio
    async def test_setup_admin_commands(self):
        mock_bot = Mock()
        mock_bot.command = Mock()

        await setup_admin_commands(mock_bot)

        assert mock_bot.command.call_count == 1
        assert mock_bot.command.call_args[1].get('name') == 'restart'

    @pytest.mark.asyncio
    async def test_restart_command(self):
        bot = commands.Bot(command_prefix='!', intents=discord.Intents.default())
        await setup_admin_commands(bot)

        ctx = Mock()
        ctx.send = AsyncMock()

        with patch('commands.admin.os.execv') as mock_execv:
            await bot.get_command('restart').callback(ctx)

        ctx.send.assert_called_once_with("Restarting...")
        mock_execv.assert_called_once()

    @pytest.mark.asyncio
    async def test_restart_is_owner_only(self):
        bot = commands.Bot(command_prefix='!', intents=discord.Intents.default())
        await setup_admin_commands(bot)

        restart_cmd = bot.get_command('restart')
        assert len(restart_cmd.checks) > 0


class TestVoiceCommands:
    """Test voice-related bot commands."""

    @pytest.mark.asyncio
    async def test_setup_voice_commands(self):
        mock_bot = Mock()
        mock_bot.command = Mock()

        await setup_voice_commands(mock_bot)

        assert mock_bot.command.call_count == 1
        assert mock_bot.command.call_args[1].get('name') == 'join'

    @pytest.mark.asyncio
    async def test_join_user_in_voice(self):
        bot = commands.Bot(command_prefix='!', intents=discord.Intents.default())
        await setup_voice_commands(bot)

        mock_channel = Mock()
        mock_channel.name = "General Voice"
        mock_channel.connect = AsyncMock()

        ctx = Mock()
        ctx.send = AsyncMock()
        ctx.author.voice = Mock()
        ctx.author.voice.channel = mock_channel

        await bot.get_command('join').callback(ctx)

        mock_channel.connect.assert_called_once()
        ctx.send.assert_called_once_with("Joined General Voice!")

    @pytest.mark.asyncio
    async def test_join_user_not_in_voice(self):
        bot = commands.Bot(command_prefix='!', intents=discord.Intents.default())
        await setup_voice_commands(bot)

        ctx = Mock()
        ctx.send = AsyncMock()
        ctx.author.voice = None

        await bot.get_command('join').callback(ctx)

        ctx.send.assert_called_once_with("You are not connected to a voice channel.")

    @pytest.mark.asyncio
    async def test_join_connection_error(self):
        bot = commands.Bot(command_prefix='!', intents=discord.Intents.default())
        await setup_voice_commands(bot)

        mock_channel = Mock()
        mock_channel.connect = AsyncMock(side_effect=discord.ClientException("failed"))

        ctx = Mock()
        ctx.send = AsyncMock()
        ctx.author.voice = Mock()
        ctx.author.voice.channel = mock_channel

        with pytest.raises(discord.ClientException):
            await bot.get_command('join').callback(ctx)


class TestCommandIntegration:
    """Test all commands together."""

    @pytest.mark.asyncio
    async def test_all_commands_registered(self):
        bot = commands.Bot(command_prefix='!', intents=discord.Intents.default())
        await setup_basic_commands(bot)
        await setup_admin_commands(bot)
        await setup_voice_commands(bot)
        await setup_tts_commands(bot)

        for name in ['hello', 'ping', '🏓', 'echo', 'restart', 'join', 'say', 'leave']:
            assert bot.get_command(name) is not None, f"'{name}' not registered"

    @pytest.mark.asyncio
    async def test_command_help_text(self):
        bot = commands.Bot(command_prefix='!', intents=discord.Intents.default())
        await setup_basic_commands(bot)
        await setup_admin_commands(bot)
        await setup_voice_commands(bot)
        await setup_tts_commands(bot)

        assert bot.get_command('echo').help == "Repeats the user's message."
        assert bot.get_command('join').help == "Joins the voice channel you are in."
        assert bot.get_command('🏓').help == "Pong"
        assert bot.get_command('restart').help == "Restarts the bot. Owner only."
        assert bot.get_command('say').help == "Speaks text in your voice channel."
        assert bot.get_command('leave').help == "Leaves the voice channel."
