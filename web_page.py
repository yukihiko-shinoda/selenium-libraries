"""The module of web page."""

from logging import getLogger

from seleniumlibraries.browser import Browser


# Reason: This is a base class. pylint: disable=too-few-public-methods
class WebPage:
    def __init__(self, browser: Browser) -> None:
        self.logger = getLogger(__name__)
        self.browser = browser
