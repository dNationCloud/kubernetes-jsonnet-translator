import logging
from translator.logger import get_logger

import pytest

def test_logger():
	result = get_logger()
	assert result == logging.getLogger("translator")
