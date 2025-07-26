"""Configuration of pytest."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import Mock

import pytest

from seleniumlibraries.browser import Browser
from seleniumlibraries.browser import DownloadWaiter

if TYPE_CHECKING:
    from collections.abc import Generator

collect_ignore = ["setup.py"]


@pytest.fixture
def fixture_browser() -> Generator[Browser]:
    """Create a real Browser for testing.

    Uses a real Browser instance instead of Mock to provide more realistic testing.
    This provides several benefits:
    - Tests actual Browser initialization and behavior
    - Verifies real Browser class works as expected
    - Provides better integration testing coverage
    - Ensures WebPage works with actual Browser instances

    Note: This requires Chrome WebDriver to be available in the test environment
    and adds browser startup overhead, but provides more confidence in the tests.
    """
    with Browser() as browser:
        yield browser


@pytest.fixture
def mock_element(text: str) -> Mock:
    """Create a mock element for testing element.py functionality.

    Uses Mock to test text extraction logic without requiring real DOM elements. This allows testing of various text
    retrieval scenarios (text, innerText, textContent) in a controlled manner. The mock provides predictable responses
    for different fallback conditions, enabling comprehensive testing of the get_text() function's robustness across
    different element states and browser behaviors.

    REPLACEMENT ANALYSIS: DIFFICULT to replace with real WebElements. The tests require
    precise control over element.text, innerText, and textContent attributes to test various
    fallback scenarios (empty strings, None values, different combinations). Real WebElements
    would require creating specific HTML with various edge cases and would be much more complex
    to set up. The Mock approach is actually more thorough for testing the fallback logic.
    """
    mock = Mock()
    mock.text = text
    mock.get_attribute = Mock(return_value=None)
    return mock


@pytest.fixture
def mock_download_waiter(tmp_path: Path) -> DownloadWaiter:
    """Create a real DownloadWaiter for testing.

    Uses a real DownloadWaiter instance with a temporary directory instead of Mock.
    This provides more realistic testing by:
    - Using actual file system operations
    - Testing real DownloadWaiter initialization and behavior
    - Providing better integration testing coverage
    - Ensuring the real class works as expected

    Args:
        tmp_path: pytest temporary directory fixture

    Returns:
        A real DownloadWaiter instance configured with the temporary directory
    """
    download_waiter = DownloadWaiter(tmp_path)
    # Mocking the wait method to avoid actual waiting in tests
    download_waiter.wait = Mock()  # type: ignore[method-assign]
    return download_waiter


@pytest.fixture
def html_loaded_browser(
    # Reason: References fixture pylint: disable-next=redefined-outer-name
    fixture_browser: Browser,
    resource_path: Path,
) -> Browser:
    """Create a Browser instance and load the specified HTML file."""
    html_path = Path(f"{resource_path}.html")
    fixture_browser.driver.get(f"file://{html_path}")
    return fixture_browser


@pytest.fixture
def common_html_loaded_browser(
    # Reason: References fixture pylint: disable-next=redefined-outer-name
    fixture_browser: Browser,
    resource_path_root: Path,
    html_file: Path,
) -> Browser:
    """Create a Browser instance and load the specified HTML file."""
    html_path = resource_path_root / html_file
    fixture_browser.driver.get(f"file://{html_path}")
    return fixture_browser
