"""Run subprocesses."""

import logging
from subprocess import PIPE, STDOUT, Popen
from typing import IO, List

logger = logging.getLogger(__name__)


def call(command: List[str]) -> int:
    """Call a command using :py:class:`subprocess.Popen`.

    The standard output of the call will be logged at the INFO level.

    Args:
        command (list[str]): The command to execute.

    Returns:
        int: The return code of the process.
    """

    def log_subprocess_output(pipe: IO[bytes]) -> None:
        for line in iter(pipe.readline, b""):  # b'\n'-separated lines
            logger.info(line.decode("utf-8").strip("\n"))

    process = Popen(command, stdout=PIPE, stderr=STDOUT)
    if process.stdout:
        with process.stdout:
            log_subprocess_output(process.stdout)
    return process.wait()
