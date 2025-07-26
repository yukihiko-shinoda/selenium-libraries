"""Tests for page.py."""

from __future__ import annotations

import logging

from seleniumlibraries.browser import Browser
from seleniumlibraries.page import WebPage


class TestWebPage:
    """Test cases for WebPage base class."""

    def test_webpage_initialization(self, fixture_browser: Browser) -> None:
        """Test WebPage initializes with browser and logger."""
        page = WebPage(fixture_browser)

        assert page.browser is fixture_browser
        assert isinstance(page.logger, logging.Logger)
        assert page.logger.name == "seleniumlibraries.page"

    def test_webpage_logger_configuration(self, fixture_browser: Browser) -> None:
        """Test WebPage logger is properly configured."""
        page = WebPage(fixture_browser)

        # Verify logger is using the correct module name
        assert page.logger.name == "seleniumlibraries.page"
        # Verify logger is an instance of Logger
        assert isinstance(page.logger, logging.Logger)

    def test_webpage_browser_assignment(self, fixture_browser: Browser) -> None:
        """Test WebPage correctly assigns browser instance."""
        page = WebPage(fixture_browser)

        assert page.browser is fixture_browser
        assert hasattr(page.browser, "driver")
        assert hasattr(page.browser, "wait")

    def test_webpage_with_different_browsers(self, fixture_browser: Browser) -> None:
        """Test WebPage works with different browser instances."""
        with Browser() as browser2:
            page1 = WebPage(fixture_browser)
            page2 = WebPage(browser2)

            assert page1.browser is fixture_browser
            assert page2.browser is browser2
            assert page1.browser is not page2.browser

    def test_webpage_inheritance_pattern(self, fixture_browser: Browser) -> None:
        """Test WebPage can be inherited for specific page implementations."""

        # Reason: To setup mock pylint: disable=too-few-public-methods
        class LoginPage(WebPage):
            def __init__(self, browser: Browser) -> None:
                super().__init__(browser)
                self.username_field = "username"

        login_page = LoginPage(fixture_browser)

        # Verify inheritance works
        assert isinstance(login_page, WebPage)
        assert login_page.browser is fixture_browser
        assert hasattr(login_page, "logger")
        assert login_page.username_field == "username"
