"""IMAP client for receiving Amazon notification emails."""
from __future__ import annotations

import asyncio
import logging
from datetime import date, timedelta
from typing import Any, Callable

import aioimaplib

from .const import DEFAULT_IMAP_FOLDER
from .email_parser import AmazonEmailParser, build_imap_search_query

_LOGGER = logging.getLogger(__name__)

# IMAP IDLE timeout - RFC recommends <30 minutes
IDLE_TIMEOUT = 29 * 60  # 29 minutes in seconds

# Reconnect backoff
INITIAL_BACKOFF = 30  # seconds
MAX_BACKOFF = 600  # 10 minutes


class ImapClient:
    """IMAP client with IDLE support for push notifications."""

    def __init__(
        self,
        server: str,
        port: int,
        email_addr: str,
        password: str,
        ssl: bool = True,
        folder: str = DEFAULT_IMAP_FOLDER,
        domains: list[str] | None = None,
        on_new_packages: Callable[[list[dict[str, Any]]], None] | None = None,
    ) -> None:
        """Initialize the IMAP client."""
        self._server = server
        self._port = port
        self._email = email_addr
        self._password = password
        self._ssl = ssl
        self._folder = folder
        self._parser = AmazonEmailParser(domains or [])
        self._domains = domains or []
        self._on_new_packages = on_new_packages

        self._client: aioimaplib.IMAP4_SSL | aioimaplib.IMAP4 | None = None
        self._idle_task: asyncio.Task | None = None
        self._running = False
        self._backoff = INITIAL_BACKOFF

    async def connect(self) -> None:
        """Connect to the IMAP server."""
        try:
            if self._ssl:
                self._client = aioimaplib.IMAP4_SSL(
                    host=self._server,
                    port=self._port,
                )
            else:
                self._client = aioimaplib.IMAP4(
                    host=self._server,
                    port=self._port,
                )

            await self._client.wait_hello_from_server()
            response = await self._client.login(self._email, self._password)

            if response.result != "OK":
                raise ConnectionError(f"Login failed: {response.result}")

            response = await self._client.select(self._folder)
            if response.result != "OK":
                raise ConnectionError(f"Failed to select folder {self._folder}")

            self._backoff = INITIAL_BACKOFF
            _LOGGER.info("Connected to IMAP server %s", self._server)

        except Exception as err:
            _LOGGER.error("Failed to connect to IMAP server: %s", err)
            self._client = None
            raise

    async def disconnect(self) -> None:
        """Disconnect from the IMAP server."""
        self._running = False

        if self._idle_task and not self._idle_task.done():
            self._idle_task.cancel()
            try:
                await self._idle_task
            except asyncio.CancelledError:
                pass
            self._idle_task = None

        if self._client:
            try:
                await self._client.logout()
            except Exception:
                pass
            self._client = None

        _LOGGER.debug("Disconnected from IMAP server")

    async def start_idle(self) -> None:
        """Start the IMAP IDLE loop as a background task."""
        self._running = True
        self._idle_task = asyncio.create_task(self._idle_loop())

    async def _idle_loop(self) -> None:
        """IMAP IDLE loop - waits for new emails."""
        while self._running:
            try:
                if not self._client:
                    await self._reconnect()
                    if not self._client:
                        continue

                idle_response = await self._client.idle_start(
                    timeout=IDLE_TIMEOUT
                )

                # Wait for IDLE to complete (new mail or timeout)
                msg = await self._client.wait_server_push()

                await self._client.idle_done()

                # Check if we got new messages
                for line in msg:
                    if isinstance(line, bytes):
                        line = line.decode("utf-8", errors="replace")
                    if "EXISTS" in str(line) or "RECENT" in str(line):
                        _LOGGER.debug("New email detected via IDLE")
                        await self._fetch_new_emails()
                        break

            except asyncio.CancelledError:
                _LOGGER.debug("IDLE loop cancelled")
                return
            except Exception as err:
                _LOGGER.warning("IDLE loop error: %s", err)
                self._client = None
                if self._running:
                    await self._reconnect()

    async def _fetch_new_emails(self) -> None:
        """Fetch and parse new emails."""
        if not self._client:
            return

        try:
            since_date = date.today() - timedelta(days=1)
            query = build_imap_search_query(self._domains, since_date)

            response = await self._client.search(query)
            if response.result != "OK":
                _LOGGER.warning("IMAP search failed: %s", response.result)
                return

            message_ids = response.lines[0].split()
            if not message_ids:
                return

            # Only fetch the last few messages (most recent)
            recent_ids = message_ids[-10:]

            packages = []
            for msg_id in recent_ids:
                msg_id_str = msg_id if isinstance(msg_id, str) else msg_id.decode()
                fetch_response = await self._client.fetch(
                    msg_id_str, "(RFC822)"
                )
                if fetch_response.result == "OK":
                    for line in fetch_response.lines:
                        if isinstance(line, bytes) and len(line) > 100:
                            pkg = self._parser.parse_email(line)
                            if pkg:
                                packages.append(pkg)

            if packages and self._on_new_packages:
                self._on_new_packages(packages)

        except Exception as err:
            _LOGGER.error("Error fetching new emails: %s", err)

    async def fetch_existing_emails(self, since_days: int = 14) -> list[dict[str, Any]]:
        """Scan existing emails from the last N days."""
        if not self._client:
            return []

        try:
            since_date = date.today() - timedelta(days=since_days)
            query = build_imap_search_query(self._domains, since_date)

            response = await self._client.search(query)
            if response.result != "OK":
                _LOGGER.warning("IMAP search failed: %s", response.result)
                return []

            message_ids = response.lines[0].split()
            _LOGGER.debug("Found %d emails to scan", len(message_ids))

            packages = []
            for msg_id in message_ids:
                msg_id_str = msg_id if isinstance(msg_id, str) else msg_id.decode()
                fetch_response = await self._client.fetch(
                    msg_id_str, "(RFC822)"
                )
                if fetch_response.result == "OK":
                    for line in fetch_response.lines:
                        if isinstance(line, bytes) and len(line) > 100:
                            pkg = self._parser.parse_email(line)
                            if pkg:
                                packages.append(pkg)

            _LOGGER.info("Parsed %d packages from existing emails", len(packages))
            return packages

        except Exception as err:
            _LOGGER.error("Error fetching existing emails: %s", err)
            return []

    async def _reconnect(self) -> None:
        """Reconnect with exponential backoff."""
        if not self._running:
            return

        _LOGGER.info(
            "Reconnecting to IMAP in %d seconds...", self._backoff
        )
        await asyncio.sleep(self._backoff)

        try:
            if self._client:
                try:
                    await self._client.logout()
                except Exception:
                    pass
                self._client = None

            await self.connect()
        except Exception as err:
            _LOGGER.warning("Reconnection failed: %s", err)
            self._backoff = min(self._backoff * 2, MAX_BACKOFF)

    @staticmethod
    async def test_connection(
        server: str,
        port: int,
        email_addr: str,
        password: str,
        ssl: bool = True,
        folder: str = DEFAULT_IMAP_FOLDER,
    ) -> bool:
        """Test IMAP connection for config flow validation."""
        client = None
        try:
            if ssl:
                client = aioimaplib.IMAP4_SSL(host=server, port=port)
            else:
                client = aioimaplib.IMAP4(host=server, port=port)

            await client.wait_hello_from_server()
            response = await client.login(email_addr, password)
            if response.result != "OK":
                return False

            response = await client.select(folder)
            if response.result != "OK":
                return False

            await client.logout()
            return True

        except Exception as err:
            _LOGGER.debug("Connection test failed: %s", err)
            return False
        finally:
            if client:
                try:
                    await client.logout()
                except Exception:
                    pass
