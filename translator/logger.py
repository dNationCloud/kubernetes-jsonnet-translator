#
# Copyright 2020 The dNation Jsonnet Translator Authors. All Rights Reserved.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import logging
import logging.handlers
import sys

from pythonjsonlogger import jsonlogger


LOGGER_NAME = "translator"
LOG_FORMAT = "%(asctime)s - [%(levelname)-5s] - %(message)s"
FORMATTER = {
    "default": logging.Formatter(LOG_FORMAT),
    "json": jsonlogger.JsonFormatter(LOG_FORMAT),
}


def get_logger():
    return logging.getLogger(LOGGER_NAME)


def get_console_handler(formatter):
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    return console_handler


def set_logger(level, format):
    """Sets the threshold for the logger to defined level and format

    Args:
        level (str): Logger threshold.
        format (str): Logger format.

    Return:
        None
    """
    formatter = FORMATTER[format]
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(level)
    logger.addHandler(get_console_handler(formatter))
    logger.propagate = False
