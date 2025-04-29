"""The package about Selenium library."""

from selenium.webdriver.remote.webelement import WebElement


def get_text(element: WebElement) -> str:
    """Gets Selenium element text.

    - Answer: python - Selenium returns empty string instead of the actual data - Stack Overflow
      https://stackoverflow.com/a/68737909/12721873
    Args:
        element: Selenium web element
    Returns: Text of the element
    """
    text = element.text
    if text:
        return text
    inner_text = element.get_attribute("innerText")
    if inner_text:
        return inner_text
    text_content = element.get_attribute("textContent")
    if text_content:
        return text_content
    return ""
