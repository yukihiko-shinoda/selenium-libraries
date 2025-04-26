"""The module about browser."""

import base64
import getpass
from pathlib import Path
import time
from types import TracebackType
from typing import Any, Optional

from selenium.webdriver import ActionChains, Chrome, ChromeOptions
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.expected_conditions import presence_of_element_located
from selenium.webdriver.support.wait import WebDriverWait


class DownloadWaiter:
    """Waiter for download.

    - Answer: python selenium, find out when a download has completed? - Stack Overflow
      https://stackoverflow.com/a/51949811/12721873
    """

    def __init__(self, directory_download: Path, nfiles: int | None = None) -> None:
        self.seconds = 0
        self.waiting = True
        self.directory_download = directory_download
        self.nfiles = nfiles

    def wait(self, timeout: int) -> None:
        while self.waiting and self.seconds < timeout:
            self._wait()

    def _wait(self) -> None:
        time.sleep(0.5)
        self.waiting = False
        files = list(self.directory_download.iterdir())
        if self.nfiles and len(files) != self.nfiles:
            self.waiting = True
        for fname in files:
            if str(fname).endswith(".crdownload"):
                self.waiting = True
        self.seconds += 1


class Browser:
    """The browser."""

    DIRECTORY_DOWNLOAD = Path("/workspace/downloads")

    def __init__(self) -> None:
        if getpass.getuser() == "root":
            msg = (
                "Selenium can't be run as root and shouldn't be used with option: `--no-sandbox` for security. "
                "Use command `sudo -u <user> pipenv run pytest`."
            )
            raise RuntimeError(msg)
        options = ChromeOptions()
        # Reason: URL too long.
        # - herokuでselenium利用時にクラッシュする場合の解決方法 #Python - Qiita
        #   https://qiita.com/kozasa/items/8a9d181e43fa0a85f6e5#%EF%BC%91-selenium%E3%81%AE%E5%BC%95%E6%95%B0%E3%81%AB%E7%9C%81%E3%83%A1%E3%83%A2%E3%83%AA%E5%8C%96%E3%81%99%E3%82%8B%E3%81%9F%E3%82%81%E3%81%AE%E5%BC%95%E6%95%B0%E3%82%92%E3%81%A4%E3%81%91%E3%82%8B)  pylint: disable=line-too-long  # noqa: E501
        # Reason: Selenium's issue.
        options.add_argument("--headless")  # type: ignore[no-untyped-call]
        options.add_argument("--disable-gpu")  # type: ignore[no-untyped-call]
        options.add_argument("--disable-dev-shm-usage")  # type: ignore[no-untyped-call]
        # PDF印刷設定
        options.add_argument("--kiosk-printing")  # type: ignore[no-untyped-call]
        options.add_argument("--remote-debugging-port=9222")  # type: ignore[no-untyped-call]
        # User-Agent を設定しないと WAON のページがエラーページを表示する仕様になっていました
        # User-Agent の設定方法は次を参考にしました:
        # - Selenium User-Agent Guide: Changing and Rotating Headers
        #   https://brightdata.com/blog/web-data/selenium-user-agent?kw=&cpn=13950045001&utm_matchtype=&utm_matchtype=&cq_src=google_ads&cq_cmp=13950045001&cq_term=&cq_plac=&cq_net=g&cq_plt=gp&utm_term=&utm_campaign=web_data-apac-search_generic-desktop&utm_source=adwords&utm_medium=ppc&utm_content=dataset-dsa&hsa_acc=1393175403&hsa_cam=13950045001&hsa_grp=133051793747&hsa_ad=622510825433&hsa_src=g&hsa_tgt=aud-1443847472521:dsa-1665041052623&hsa_kw=&hsa_mt=&hsa_net=adwords&hsa_ver=3&gad_source=1&gclid=CjwKCAiA5eC9BhAuEiwA3CKwQg952NCF0RakDla2KFWZ5W7OyspldKq9RUaE6IIw1XPtUclAbNegCBoCz9AQAvD_BwE
        custom_user_agent = (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
        )
        options.add_argument(f"--user-agent={custom_user_agent}")  # type: ignore[no-untyped-call]
        prefs = {
            # To download files
            "download.default_directory": str(self.DIRECTORY_DOWNLOAD),
            "savefile.default_directory": str(self.DIRECTORY_DOWNLOAD),
            # # PDF印刷設定
            # "download.directory_upgrade": True,
            "download.prompt_for_download": False,
            # To download PDF instead of opening it in new tab
            "plugins.always_open_pdf_externally": True,
            # "printing.print_preview_sticky_settings.appState": json.dumps(appState),
        }
        options.add_experimental_option("prefs", prefs)
        self.driver = Chrome(options=options)
        self.driver.set_window_size(480, 600)
        self.wait = WebDriverWait(self.driver, 10)

    def __enter__(self) -> "Browser":
        return self

    def __exit__(
        self,
        _exc_type: Optional[type[BaseException]],
        _exc_value: Optional[BaseException],
        _traceback: Optional[TracebackType],
    ) -> None:
        self.driver.quit()

    def wait_for(self, by: str, value: str, *, timeout: float | None = None) -> WebElement:
        # Reason: Certainly returns WebElement.
        wait = WebDriverWait(self.driver, timeout) if timeout else self.wait
        return wait.until(presence_of_element_located((by, value)))  # type: ignore[no-any-return]

    def scroll_and_click(self, by: str, value: str) -> None:
        """Scroll to element and click it."""
        chains = ActionChains(self.driver)
        chains.move_to_element(self.wait_for(by, value)).click().perform()

    def save_as_pdf(self, path: Path, *, options: dict[str, Any] | None = None) -> None:
        """Since window.print() didn't work and couldn't debug no more."""
        # https://timvdlippe.github.io/devtools-protocol/tot/Page#method-printToPDF
        options = options or {}
        pdf_base64 = self.driver.execute_cdp_cmd("Page.printToPDF", options)
        with (self.DIRECTORY_DOWNLOAD / path).open("wb") as file:
            file.write(base64.b64decode(pdf_base64["data"]))

    def wait_for_download(self, timeout: int, number_of_files: int | None = None) -> None:
        """Wait for downloads to finish with a specified timeout.

        Args:
            directory: The path to the folder where the files will be downloaded.
            timeout: How many seconds to wait until timing out.
            number_of_files: If provided, also wait for the expected number of files.
        """
        waiter = DownloadWaiter(self.DIRECTORY_DOWNLOAD, number_of_files)
        waiter.wait(timeout)

    def wait_for_closing_tab(self, expected_number_of_tabs: int, timeout: int) -> None:
        """Wait for closing tab."""
        seconds = 0
        while len(self.driver.window_handles) > expected_number_of_tabs:
            time.sleep(0.5)
            seconds += 1
            if seconds == timeout:
                self.driver.close()
            if seconds > timeout:
                msg = "Timeout waiting for closing tab."
                raise TimeoutError(msg)
