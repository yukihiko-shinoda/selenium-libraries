"""Tests for element.py."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import pytest
from selenium.webdriver.common.by import By

from seleniumlibraries.element import get_text

if TYPE_CHECKING:
    from unittest.mock import Mock

    from seleniumlibraries.browser import Browser


@dataclass
class FallbackTestCase:
    """Test case for fallback scenarios."""

    inner_text: str | None
    text_content: str
    expected_result: str
    expected_calls: int


class TestGetText:
    """Test cases for get_text function."""

    @pytest.mark.parametrize(
        ("test_case", "text"),
        [
            # Test fallback to innerText when text is empty
            pytest.param(
                FallbackTestCase("Inner text content", "Text content", "Inner text content", 1),
                "",
                id="to_inner_text",
            ),
            # Test fallback to textContent when text and innerText are empty
            pytest.param(
                FallbackTestCase("", "Text content fallback", "Text content fallback", 2),
                "",
                id="to_text_content",
            ),
            # Test fallback to textContent when innerText is None
            pytest.param(
                FallbackTestCase(None, "Text content from none", "Text content from none", 2),
                "",
                id="when_inner_text_none",
            ),
        ],
    )
    def test_get_text_fallback_scenarios(self, mock_element: Mock, test_case: FallbackTestCase) -> None:
        """Test get_text fallback scenarios."""
        mock_element.get_attribute.side_effect = {
            "innerText": test_case.inner_text,
            "textContent": test_case.text_content,
        }.get

        result = get_text(mock_element)

        assert result == test_case.expected_result
        assert mock_element.get_attribute.call_count == test_case.expected_calls

    @pytest.mark.parametrize(
        ("text", "attribute_return_value"),
        [
            # Test returns empty string when all sources are empty
            pytest.param("", "", id="all_empty"),
            # Test returns empty string when all sources are None
            pytest.param("", None, id="all_none"),
        ],
    )
    def test_get_text_empty_scenarios(
        self,
        mock_element: Mock,
        attribute_return_value: str | None,
    ) -> None:
        """Test get_text when all sources are empty or None."""
        mock_element.get_attribute.return_value = attribute_return_value

        result = get_text(mock_element)

        assert result == ""
        expected_call_count = 2
        assert mock_element.get_attribute.call_count == expected_call_count

    @pytest.mark.parametrize("text", [""])
    def test_get_text_attribute_call_sequence(self, mock_element: Mock) -> None:
        """Test get_text calls attributes in correct sequence."""
        call_log = []

        def track_calls(attr: str) -> None:
            call_log.append(attr)

        mock_element.get_attribute.side_effect = track_calls

        result = get_text(mock_element)

        assert result == ""
        assert call_log == ["innerText", "textContent"]

    def test(self, html_loaded_browser: Browser) -> None:
        """Test get_text with real WebElements from HTML."""
        browser = html_loaded_browser

        # Test simple text
        simple_element = browser.driver.find_element(By.ID, "simple-text")
        assert get_text(simple_element) == "Hello World"

        # Test empty text
        empty_element = browser.driver.find_element(By.ID, "empty-text")
        assert get_text(empty_element) == ""

        # Test whitespace text
        whitespace_element = browser.driver.find_element(By.ID, "whitespace-text")
        assert get_text(whitespace_element) == "   "

        # Test nested text
        nested_element = browser.driver.find_element(By.ID, "nested-text")
        assert get_text(nested_element) == "Inner Text"
