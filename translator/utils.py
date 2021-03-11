# Copyright 2020 The dNation Jsonnet Translator Authors. All Rights Reserved.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import hashlib
import patoolib
import base64
import binascii
import shutil
from datetime import datetime

from . import logger

log = logger.get_logger()


def after_retry(retry_state):
    """Ignore exception after last retry.

    Use as callback for tenacity.retry_error_callback. After last retry
    no exception is raised.

    Args:
        retry_state (tenacity.RetryCallState): State from tenacity module.

    Returns:
        None

    """
    pass


def timestamp():
    """Returns current timestamp in format [YYYY-MM-DD hh:mm:ss].

    Args:

    Returns:
        str: Current timestamp.
    """
    return datetime.now().strftime("[%Y-%m-%d %X]")


def remove_file(folder, filename):
    """Removes file.

    Args:
        folder (str): Folder with file to remove.
        filename (str): File to be removed.

    Returns:
        None
    """
    complete_filepath = os.path.join(folder, filename)
    try:
        os.remove(complete_filepath)
        log.debug(f"File {complete_filepath} deleted")
    except FileNotFoundError:
        log.error(f"Error when removing {complete_filepath}: file not found")
    except OSError as e:
        log.error(f"Error when removing {complete_filepath}: {e}")


def remove_folder(folder):
    """Removes folder with content.

    Args:
        folder (str): Folder to remove.

    Returns:
        None
    """
    try:
        shutil.rmtree(folder)
        log.debug(f"Folder {folder} deleted")
    except OSError as e:
        log.error(f"Error when removing folder {folder}, error: {e}")


def replace_extension(full_filename, new_extension):
    """Replace extension of filename.

    Args:
        full_filename (str): Filename with extension.
        new_extension (str): New extension.

    Returns:
         str: full_filename with replaced extension.
    """
    filename, old_extension = os.path.splitext(full_filename)
    return f"{filename}.{new_extension}"


def save_text_to_file(folder, filename, text):
    """Writes text to file (only if file will be created or changed).

    Parent folder is created if doesn't exists.

    Args:
        folder (str): Folder where to save.
        filename (str): Filename where to save.
        text (str): Data to be written.

    Returns:
        None
    """
    complete_filepath = os.path.join(folder, filename)
    if os.path.exists(complete_filepath):
        sha256_hash_new = hashlib.sha256(text.encode("utf-8"))

        with open(complete_filepath, "rb") as f:
            sha256_hash_cur = hashlib.sha256(f.read())

        if sha256_hash_new.hexdigest() == sha256_hash_cur.hexdigest():
            log.debug(
                f"Content of {complete_filepath} haven't changed."
                f" Not overwriting existing file."
            )
            return

    try:
        if not os.path.exists(folder):
            os.makedirs(folder)
        with open(complete_filepath, "w") as f:
            f.write(text)
            log.debug(f"File {complete_filepath} created")
    except (OSError, IOError) as e:
        log.error(f"Error when creating dashboard {complete_filepath}, error: {e}")


def extract_archive_data(archive_data, archive_name, folder):
    """Extract and save data from compressed folder from config map.

    Args:
        archive_data (str): Base64 encoded jsonnet folder (archive).
        archive_name (str): Archive name (needed for extensions).
        folder (str): Folder that will be created and archive extracted to.

    Returns:
        None
    """
    try:
        if not os.path.exists(folder):
            os.mkdir(folder)
    except OSError as e:
        log.error(f"Error when creating folder {folder}, error: {e}")
        return

    try:
        with open(archive_name, "wb") as f:
            f.write(base64.b64decode(archive_data))
    except (binascii.Error, IOError) as e:
        log.error(f"Error when decoding {archive_name}, error: {e}")

    try:
        patoolib.extract_archive(archive_name, outdir=folder, verbosity=-1)
        log.info(f"File {archive_name} extracted to {folder}")
    except patoolib.util.PatoolError as e:
        log.error(f"Error when extracting {archive_name}, error: {e}")

    remove_file("./", archive_name)
