"""Tests for main bot functionality."""

import pytest
import os
from unittest.mock import Mock, patch, AsyncMock, PropertyMock
import discord
from discord.ext import commands

from main import create_bot, main


class TestBotCreation:
    """Test bot creation."""

    def test_create_bot_returns_bot(self):
        assert isinstance(create_bot(), commands.Bot)

    def test_create_bot_default_prefix(self):
        env = {k: v for k, v in os.environ.items() if k != 'COMMAND_PREFIX'}
        with patch.dict(os.environ, env, clear=True):
            bot = create_bot()
        assert bot.command_prefix == '!'

    def test_create_bot_custom_prefix(self):
        with patch.dict(os.environ, {'COMMAND_PREFIX': '#'}):
            bot = create_bot()
        assert bot.command_prefix == '#'

    def test_create_bot_has_event_handlers(self):
        bot = create_bot()
        assert hasattr(bot, 'on_ready')
        assert hasattr(bot, 'on_command_error')

    def test_create_bot_has_setup_hook(self):
        bot = create_bot()
        assert callable(bot.setup_hook)


class TestBotEvents:
    """Test bot event handlers."""

    @pytest.mark.asyncio
    async def test_on_ready(self):
        bot = create_bot()
        with patch.object(type(bot), 'user', new_callable=PropertyMock) as mock_user:
            mock_user.return_value = Mock(id=123456789)
            await bot.on_ready()  # should not raise

    @pytest.mark.asyncio
    async def test_on_command_error_not_owner(self):
        bot = create_bot()
        ctx = Mock()
        ctx.send = AsyncMock()
        ctx.command = 'restart'

        await bot.on_command_error(ctx, commands.NotOwner())

        ctx.send.assert_called_once()
        assert "owner" in ctx.send.call_args[0][0].lower()

    @pytest.mark.asyncio
    async def test_on_command_error_command_not_found(self):
        """CommandNotFound should be silently ignored."""
        bot = create_bot()
        ctx = Mock()
        ctx.send = AsyncMock()

        await bot.on_command_error(ctx, commands.CommandNotFound('foo'))

        ctx.send.assert_not_called()

    @pytest.mark.asyncio
    async def test_on_command_error_missing_argument(self):
        bot = create_bot()
        ctx = Mock()
        ctx.send = AsyncMock()
        ctx.command = 'echo'

        param = Mock()
        param.name = 'message'
        await bot.on_command_error(ctx, commands.MissingRequiredArgument(param))

        ctx.send.assert_called_once()
        assert "message" in ctx.send.call_args[0][0]

    @pytest.mark.asyncio
    async def test_on_command_error_unexpected(self):
        bot = create_bot()
        ctx = Mock()
        ctx.send = AsyncMock()
        ctx.command = 'echo'

        await bot.on_command_error(ctx, ValueError("something broke"))

        ctx.send.assert_called_once()
        assert "unexpected" in ctx.send.call_args[0][0].lower()


class TestMainFunction:
    """Test main entry point."""

    @patch('main.load_dotenv')
    @patch('main.create_bot')
    def test_main_runs_bot(self, mock_create_bot, mock_load_dotenv):
        mock_bot = Mock()
        mock_create_bot.return_value = mock_bot

        with patch.dict(os.environ, {'DISCORD_BOT_TOKEN': 'test_token'}):
            main()

        mock_bot.run.assert_called_once_with('test_token')
        mock_load_dotenv.assert_called_once()

    @patch('main.load_dotenv')
    def test_main_no_token_exits(self, mock_load_dotenv):
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(SystemExit):
                main()
