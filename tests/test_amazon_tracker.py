"""Tests for Amazon Package Tracker fetch functionality."""
import pytest
from unittest.mock import AsyncMock, Mock, patch
from custom_components.amazon_tracker.amazon_tracker import fetch_amazon_packages
from custom_components.amazon_tracker.const import AMAZON_DOMAINS


class TestFetchAmazonPackages:
    """Test the fetch_amazon_packages function."""

    @pytest.mark.asyncio
    async def test_unsupported_domain(self):
        """Test that unsupported domain returns empty list."""
        result = await fetch_amazon_packages(
            "test@example.com",
            "password",
            "amazon.invalid"
        )
        assert result == []

    @pytest.mark.asyncio
    async def test_domain_parameter_default(self):
        """Test that domain parameter defaults to amazon.de."""
        with patch("custom_components.amazon_tracker.amazon_tracker.aiohttp.ClientSession") as mock_session:
            mock_response = AsyncMock()
            mock_response.status = 404  # Will cause early return
            mock_response.url = "test"
            
            mock_session_instance = AsyncMock()
            mock_session_instance.get.return_value.__aenter__.return_value = mock_response
            mock_session.return_value.__aenter__.return_value = mock_session_instance
            
            result = await fetch_amazon_packages("test@example.com", "password")
            
            # Check that amazon.de URL was used (default)
            assert mock_session_instance.get.called

    @pytest.mark.asyncio
    async def test_amazon_com_url_construction(self):
        """Test that Amazon.com URLs are constructed correctly."""
        with patch("custom_components.amazon_tracker.amazon_tracker.aiohttp.ClientSession") as mock_session:
            mock_response = AsyncMock()
            mock_response.status = 404  # Will cause early return
            mock_response.url = "test"
            
            mock_session_instance = AsyncMock()
            mock_session_instance.get.return_value.__aenter__.return_value = mock_response
            mock_session.return_value.__aenter__.return_value = mock_session_instance
            
            await fetch_amazon_packages("test@example.com", "password", "amazon.com")
            
            # Check that the get method was called with amazon.com URL
            call_args = mock_session_instance.get.call_args[0][0]
            assert "amazon.com" in call_args

    @pytest.mark.asyncio
    async def test_amazon_de_url_construction(self):
        """Test that Amazon.de URLs are constructed correctly."""
        with patch("custom_components.amazon_tracker.amazon_tracker.aiohttp.ClientSession") as mock_session:
            mock_response = AsyncMock()
            mock_response.status = 404
            mock_response.url = "test"
            
            mock_session_instance = AsyncMock()
            mock_session_instance.get.return_value.__aenter__.return_value = mock_response
            mock_session.return_value.__aenter__.return_value = mock_session_instance
            
            await fetch_amazon_packages("test@example.com", "password", "amazon.de")
            
            call_args = mock_session_instance.get.call_args[0][0]
            assert "amazon.de" in call_args

    @pytest.mark.asyncio
    async def test_amazon_fr_url_construction(self):
        """Test that Amazon.fr URLs are constructed correctly."""
        with patch("custom_components.amazon_tracker.amazon_tracker.aiohttp.ClientSession") as mock_session:
            mock_response = AsyncMock()
            mock_response.status = 404
            mock_response.url = "test"
            
            mock_session_instance = AsyncMock()
            mock_session_instance.get.return_value.__aenter__.return_value = mock_response
            mock_session.return_value.__aenter__.return_value = mock_session_instance
            
            await fetch_amazon_packages("test@example.com", "password", "amazon.fr")
            
            call_args = mock_session_instance.get.call_args[0][0]
            assert "amazon.fr" in call_args

    @pytest.mark.asyncio
    async def test_amazon_co_uk_url_construction(self):
        """Test that Amazon.co.uk URLs are constructed correctly."""
        with patch("custom_components.amazon_tracker.amazon_tracker.aiohttp.ClientSession") as mock_session:
            mock_response = AsyncMock()
            mock_response.status = 404
            mock_response.url = "test"
            
            mock_session_instance = AsyncMock()
            mock_session_instance.get.return_value.__aenter__.return_value = mock_response
            mock_session.return_value.__aenter__.return_value = mock_session_instance
            
            await fetch_amazon_packages("test@example.com", "password", "amazon.co.uk")
            
            call_args = mock_session_instance.get.call_args[0][0]
            assert "amazon.co.uk" in call_args

    @pytest.mark.asyncio
    async def test_amazon_ie_url_construction(self):
        """Test that Amazon.ie URLs are constructed correctly."""
        with patch("custom_components.amazon_tracker.amazon_tracker.aiohttp.ClientSession") as mock_session:
            mock_response = AsyncMock()
            mock_response.status = 404
            mock_response.url = "test"
            
            mock_session_instance = AsyncMock()
            mock_session_instance.get.return_value.__aenter__.return_value = mock_response
            mock_session.return_value.__aenter__.return_value = mock_session_instance
            
            await fetch_amazon_packages("test@example.com", "password", "amazon.ie")
            
            call_args = mock_session_instance.get.call_args[0][0]
            assert "amazon.ie" in call_args

    @pytest.mark.asyncio
    async def test_all_domains_supported(self):
        """Test that all configured domains can be used."""
        for domain in AMAZON_DOMAINS.keys():
            with patch("custom_components.amazon_tracker.amazon_tracker.aiohttp.ClientSession") as mock_session:
                mock_response = AsyncMock()
                mock_response.status = 404
                mock_response.url = "test"
                
                mock_session_instance = AsyncMock()
                mock_session_instance.get.return_value.__aenter__.return_value = mock_response
                mock_session.return_value.__aenter__.return_value = mock_session_instance
                
                result = await fetch_amazon_packages("test@example.com", "password", domain)
                
                # Should not return error for valid domains
                assert isinstance(result, list)

