from logging import getLogger

from etaxarchivemessagebox.selenium.browser import Browser


# Reason: This is a base class. pylint: disable=too-few-public-methods
class WebPage:
    def __init__(self, browser: Browser) -> None:
        self.logger = getLogger(__name__)
        self.browser = browser
