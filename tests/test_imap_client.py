"""Tests for IMAP client."""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from custom_components.amazon_tracker.imap_client import ImapClient


class TestImapClient:
    """Test ImapClient class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.client = ImapClient(
            server="imap.example.com",
            port=993,
            email_addr="user@example.com",
            password="password123",
            ssl=True,
            folder="INBOX",
            domains=["amazon.de"],
        )

    def test_initialization(self):
        """Test client initialization."""
        assert self.client._server == "imap.example.com"
        assert self.client._port == 993
        assert self.client._email == "user@example.com"
        assert self.client._ssl is True
        assert self.client._folder == "INBOX"
        assert self.client._client is None
        assert self.client._running is False

    def test_initialization_non_ssl(self):
        """Test client initialization without SSL."""
        client = ImapClient(
            server="imap.example.com",
            port=143,
            email_addr="user@example.com",
            password="password123",
            ssl=False,
        )
        assert client._ssl is False
        assert client._port == 143

    def test_callback_is_stored(self):
        """Test that the callback is stored."""
        callback = MagicMock()
        client = ImapClient(
            server="imap.example.com",
            port=993,
            email_addr="user@example.com",
            password="password123",
            on_new_packages=callback,
        )
        assert client._on_new_packages is callback

    def test_default_domains(self):
        """Test default domains is empty list."""
        client = ImapClient(
            server="imap.example.com",
            port=993,
            email_addr="user@example.com",
            password="password123",
        )
        assert client._domains == []

    @pytest.mark.asyncio
    async def test_connect_ssl(self):
        """Test SSL connection."""
        mock_imap = AsyncMock()
        mock_imap.wait_hello_from_server = AsyncMock()
        mock_imap.login = AsyncMock(return_value=MagicMock(result="OK"))
        mock_imap.select = AsyncMock(return_value=MagicMock(result="OK"))

        with patch("custom_components.amazon_tracker.imap_client.aioimaplib") as mock_lib:
            mock_lib.IMAP4_SSL = MagicMock(return_value=mock_imap)
            await self.client.connect()

        assert self.client._client is not None
        mock_imap.login.assert_called_once_with("user@example.com", "password123")
        mock_imap.select.assert_called_once_with("INBOX")

    @pytest.mark.asyncio
    async def test_connect_login_failure(self):
        """Test connection with login failure."""
        mock_imap = AsyncMock()
        mock_imap.wait_hello_from_server = AsyncMock()
        mock_imap.login = AsyncMock(return_value=MagicMock(result="NO"))

        with patch("custom_components.amazon_tracker.imap_client.aioimaplib") as mock_lib:
            mock_lib.IMAP4_SSL = MagicMock(return_value=mock_imap)
            with pytest.raises(ConnectionError):
                await self.client.connect()

    @pytest.mark.asyncio
    async def test_disconnect(self):
        """Test disconnection."""
        mock_imap = AsyncMock()
        mock_imap.logout = AsyncMock()
        self.client._client = mock_imap

        await self.client.disconnect()

        assert self.client._client is None
        assert self.client._running is False
        mock_imap.logout.assert_called_once()

    @pytest.mark.asyncio
    async def test_disconnect_when_not_connected(self):
        """Test disconnect when already disconnected."""
        await self.client.disconnect()
        # Should not raise

    @pytest.mark.asyncio
    async def test_fetch_existing_emails_not_connected(self):
        """Test fetch_existing_emails when not connected."""
        result = await self.client.fetch_existing_emails()
        assert result == []

    @pytest.mark.asyncio
    async def test_test_connection_success(self):
        """Test static test_connection method."""
        mock_imap = AsyncMock()
        mock_imap.wait_hello_from_server = AsyncMock()
        mock_imap.login = AsyncMock(return_value=MagicMock(result="OK"))
        mock_imap.select = AsyncMock(return_value=MagicMock(result="OK"))
        mock_imap.logout = AsyncMock()

        with patch("custom_components.amazon_tracker.imap_client.aioimaplib") as mock_lib:
            mock_lib.IMAP4_SSL = MagicMock(return_value=mock_imap)
            result = await ImapClient.test_connection(
                server="imap.example.com",
                port=993,
                email_addr="user@example.com",
                password="password123",
            )

        assert result is True

    @pytest.mark.asyncio
    async def test_test_connection_failure(self):
        """Test static test_connection with auth failure."""
        mock_imap = AsyncMock()
        mock_imap.wait_hello_from_server = AsyncMock()
        mock_imap.login = AsyncMock(return_value=MagicMock(result="NO"))
        mock_imap.logout = AsyncMock()

        with patch("custom_components.amazon_tracker.imap_client.aioimaplib") as mock_lib:
            mock_lib.IMAP4_SSL = MagicMock(return_value=mock_imap)
            result = await ImapClient.test_connection(
                server="imap.example.com",
                port=993,
                email_addr="user@example.com",
                password="wrong",
            )

        assert result is False

    @pytest.mark.asyncio
    async def test_test_connection_exception(self):
        """Test static test_connection with connection exception."""
        with patch("custom_components.amazon_tracker.imap_client.aioimaplib") as mock_lib:
            mock_lib.IMAP4_SSL = MagicMock(side_effect=Exception("Connection refused"))
            result = await ImapClient.test_connection(
                server="imap.example.com",
                port=993,
                email_addr="user@example.com",
                password="password123",
            )

        assert result is False
