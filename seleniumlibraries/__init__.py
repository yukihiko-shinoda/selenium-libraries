"""Top-level package for Selenium Libraries."""

from seleniumlibraries.browser import *  # noqa: F403
from seleniumlibraries.element import *  # noqa: F403
from seleniumlibraries.page import *  # noqa: F403

__version__ = "0.1.0"

__all__ = []
__all__ += browser.__all__  # type:ignore[name-defined] # noqa: F405 pylint: disable=undefined-variable
__all__ += element.__all__  # type:ignore[name-defined] # noqa: F405 pylint: disable=undefined-variable
__all__ += page.__all__  # type:ignore[name-defined] # noqa: F405 pylint: disable=undefined-variable
