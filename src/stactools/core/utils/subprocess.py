import logging
from subprocess import Popen, PIPE, STDOUT
from typing import IO, List

logger = logging.getLogger(__name__)


def call(command: List[str]) -> int:

    def log_subprocess_output(pipe: IO[bytes]) -> None:
        for line in iter(pipe.readline, b''):  # b'\n'-separated lines
            logger.info(line.decode("utf-8").strip('\n'))

    process = Popen(command, stdout=PIPE, stderr=STDOUT)
    if process.stdout:
        with process.stdout:
            log_subprocess_output(process.stdout)
    return process.wait()
