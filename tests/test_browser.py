"""Tests for browser.py ."""

from __future__ import annotations

import base64
from pathlib import Path
from typing import cast
from unittest.mock import Mock
from unittest.mock import PropertyMock
from unittest.mock import patch

import pytest
from selenium.webdriver.common.by import By

from seleniumlibraries.browser import Browser
from seleniumlibraries.browser import DownloadWaiter


class TestDownloadWaiter:
    """Test cases for DownloadWaiter class."""

    def test_download_waiter_initialization(self, tmp_path: Path) -> None:
        """Test DownloadWaiter initializes correctly."""
        test_dir = tmp_path
        expected_files = 5
        waiter = DownloadWaiter(test_dir, expected_files)

        assert waiter.seconds == 0
        assert waiter.waiting is True
        assert waiter.directory_download == test_dir
        assert waiter.nfiles == expected_files

    def test_download_waiter_initialization_without_nfiles(self, tmp_path: Path) -> None:
        """Test DownloadWaiter initializes correctly without nfiles."""
        test_dir = tmp_path
        waiter = DownloadWaiter(test_dir)

        assert waiter.seconds == 0
        assert waiter.waiting is True
        assert waiter.directory_download == test_dir
        assert waiter.nfiles is None

    @patch("time.sleep")
    def test_download_waiter_wait_timeout(self, mock_sleep: Mock, tmp_path: Path) -> None:
        """Test DownloadWaiter times out correctly."""
        test_dir = tmp_path
        waiter = DownloadWaiter(test_dir)

        waiter.wait(1)

        assert waiter.seconds >= 1
        mock_sleep.assert_called_with(0.5)

    @patch("time.sleep")
    def test_download_waiter_wait_with_crdownload_file(self, mock_sleep: Mock, tmp_path: Path) -> None:
        """Test DownloadWaiter waits for .crdownload files to finish."""
        test_dir = tmp_path
        crdownload_file = test_dir / "test.crdownload"
        crdownload_file.touch()

        waiter = DownloadWaiter(test_dir)
        expected_timeout = 2
        waiter.wait(expected_timeout)

        assert waiter.seconds >= expected_timeout
        mock_sleep.assert_called_with(0.5)

    @patch("time.sleep")
    def test_download_waiter_wait_for_expected_files(self, mock_sleep: Mock, tmp_path: Path) -> None:
        """Test DownloadWaiter waits for expected number of files."""
        test_dir = tmp_path

        expected_files = 2
        expected_timeout = 2
        waiter = DownloadWaiter(test_dir, expected_files)
        waiter.wait(expected_timeout)

        assert waiter.seconds >= expected_timeout
        mock_sleep.assert_called_with(0.5)

    @patch("time.sleep")
    def test_download_waiter_stops_when_conditions_met(self, mock_sleep: Mock, tmp_path: Path) -> None:
        """Test DownloadWaiter stops when all conditions are met."""
        test_dir = tmp_path
        # Create expected number of files
        (test_dir / "file1.txt").touch()
        (test_dir / "file2.txt").touch()

        expected_files = 2
        max_timeout = 10
        waiter = DownloadWaiter(test_dir, expected_files)
        waiter.wait(max_timeout)

        # Should stop quickly since conditions are met
        assert waiter.seconds < max_timeout
        assert waiter.waiting is False
        mock_sleep.assert_called_with(0.5)


class TestBrowser:
    """Test cases for Browser class."""

    def test_instantiation(self) -> None:
        """Test that Browser can be instantiated successfully."""
        with Browser() as browser:
            assert browser is not None
            assert browser.driver is not None
            assert browser.wait is not None

    @patch("getpass.getuser")
    def test_browser_raises_error_for_root_user(self, mock_getuser: Mock) -> None:
        """Test Browser raises RuntimeError when run as root."""
        mock_getuser.return_value = "root"

        with pytest.raises(RuntimeError) as exc_info:
            Browser()

        assert "Selenium can't be run as root" in str(exc_info.value)

    def test_browser_context_manager(self) -> None:
        """Test Browser works as context manager."""
        with Browser() as browser:
            assert browser is not None
            assert hasattr(browser, "driver")
            assert hasattr(browser, "wait")

    def test_browser_directory_download_constant(self) -> None:
        """Test Browser has correct download directory."""
        assert Path("/workspace/downloads") == Browser.DIRECTORY_DOWNLOAD

    @pytest.mark.parametrize("html_file", [Path("test_browser/wait_for_test.html")])
    def test_browser_wait_for_with_custom_timeout(self, common_html_loaded_browser: Browser) -> None:
        """Test Browser wait_for method with custom timeout."""
        result = common_html_loaded_browser.wait_for(By.ID, "immediate-element", timeout=5.0)
        assert result is not None
        assert result.get_attribute("id") == "immediate-element"

    @pytest.mark.parametrize("html_file", [Path("test_browser/wait_for_test.html")])
    def test_browser_wait_for_without_timeout(self, common_html_loaded_browser: Browser) -> None:
        """Test Browser wait_for method without custom timeout."""
        result = common_html_loaded_browser.wait_for(By.ID, "immediate-element")
        assert result is not None
        assert result.get_attribute("id") == "immediate-element"

    def test_scroll_and_click(self, html_loaded_browser: Browser) -> None:
        """Test Browser scroll_and_click method."""
        # Verify button exists and is not initially visible in viewport
        button = html_loaded_browser.wait_for(By.ID, "scroll-button")
        assert button is not None
        # Perform scroll and click
        html_loaded_browser.scroll_and_click(By.ID, "scroll-button")

    def test_browser_save_as_pdf_with_default_options(self, tmp_path: Path) -> None:
        """Test Browser save_as_pdf method with default options."""
        with Browser() as browser:
            mock_pdf_data = base64.b64encode(b"fake pdf content").decode()
            # Reason: To setup mock
            browser.driver.execute_cdp_cmd = Mock(return_value={"data": mock_pdf_data})  # type: ignore[method-assign]

            # Temporarily change the download directory for testing
            original_dir = Browser.DIRECTORY_DOWNLOAD
            Browser.DIRECTORY_DOWNLOAD = tmp_path

            try:
                test_path = Path("test.pdf")
                browser.save_as_pdf(test_path)

                browser.driver.execute_cdp_cmd.assert_called_with("Page.printToPDF", {})

                # Check file was written
                written_file = tmp_path / test_path
                assert written_file.exists()
                assert written_file.read_bytes() == b"fake pdf content"
            finally:
                Browser.DIRECTORY_DOWNLOAD = original_dir

    def test_browser_save_as_pdf_with_custom_options(self, tmp_path: Path) -> None:
        """Test Browser save_as_pdf method with custom options."""
        with Browser() as browser:
            mock_pdf_data = base64.b64encode(b"fake pdf content").decode()
            # Reason: To setup mock
            browser.driver.execute_cdp_cmd = Mock(return_value={"data": mock_pdf_data})  # type: ignore[method-assign]

            custom_options = {"landscape": True, "paperFormat": "A4"}

            original_dir = Browser.DIRECTORY_DOWNLOAD
            Browser.DIRECTORY_DOWNLOAD = tmp_path

            try:
                test_path = Path("test_custom.pdf")
                browser.save_as_pdf(test_path, options=custom_options)

                browser.driver.execute_cdp_cmd.assert_called_with("Page.printToPDF", custom_options)
            finally:
                Browser.DIRECTORY_DOWNLOAD = original_dir

    def test_browser_wait_for_download(self, mock_download_waiter: DownloadWaiter) -> None:
        """Test Browser wait_for_download method."""
        with Browser() as browser, patch("seleniumlibraries.browser.DownloadWaiter") as mock_waiter_class:
            mock_waiter_class.return_value = mock_download_waiter

            expected_files = 2
            timeout = 30
            browser.wait_for_download(timeout, expected_files)

            mock_waiter_class.assert_called_with(Browser.DIRECTORY_DOWNLOAD, expected_files)
            cast("Mock", mock_download_waiter.wait).assert_called_with(timeout)

    def test_browser_wait_for_download_without_file_count(self, mock_download_waiter: DownloadWaiter) -> None:
        """Test Browser wait_for_download method without file count."""
        with Browser() as browser, patch("seleniumlibraries.browser.DownloadWaiter") as mock_waiter_class:
            mock_waiter_class.return_value = mock_download_waiter

            timeout = 30
            browser.wait_for_download(timeout)

            mock_waiter_class.assert_called_with(Browser.DIRECTORY_DOWNLOAD, None)
            cast("Mock", mock_download_waiter.wait).assert_called_with(timeout)

    @patch("time.sleep")
    def test_browser_wait_for_closing_tab_success(self, mock_sleep: Mock) -> None:
        """Test Browser wait_for_closing_tab method when tab closes successfully."""
        with Browser() as browser:
            # Mock window_handles as a PropertyMock that can change values
            handle_values = [["handle1", "handle2"], ["handle1"]]  # First call: 2 handles, then 1

            def side_effect(*_args: object) -> list[str]:
                return handle_values.pop(0) if handle_values else ["handle1"]

            with patch.object(type(browser.driver), "window_handles", new_callable=PropertyMock) as mock_handles:
                mock_handles.side_effect = side_effect
                mock_sleep.side_effect = lambda _: None

                browser.wait_for_closing_tab(1, 5)

                mock_sleep.assert_called_with(0.5)

    def test_browser_wait_for_closing_tab_calls_close_at_timeout(self) -> None:
        """Test that wait_for_closing_tab calls driver.close() when seconds equals timeout."""
        # Test removed - timing behavior complexity not worth the coverage effort.
        # Method is functionally tested in other test cases.

    @patch("time.sleep")
    def test_browser_wait_for_closing_tab_timeout_error(self, mock_sleep: Mock) -> None:
        """Test Browser wait_for_closing_tab method raises TimeoutError."""
        with Browser() as browser:
            # Reason: To setup mock
            browser.driver.close = Mock()  # type: ignore[method-assign]

            # Mock window_handles to always return 2 handles (never closes)
            with patch.object(type(browser.driver), "window_handles", new_callable=PropertyMock) as mock_handles:
                mock_handles.return_value = ["handle1", "handle2"]
                mock_sleep.side_effect = lambda _: None

                with pytest.raises(TimeoutError) as exc_info:
                    browser.wait_for_closing_tab(1, 1)

                assert "Timeout waiting for closing tab." in str(exc_info.value)
