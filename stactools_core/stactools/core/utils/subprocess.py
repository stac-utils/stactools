import logging
from subprocess import Popen, PIPE, STDOUT
from typing import List

logger = logging.getLogger(__name__)


def call(command: List[str]) -> int:
    def log_subprocess_output(pipe):
        for line in iter(pipe.readline, b''):  # b'\n'-separated lines
            logger.info(line.decode("utf-8").strip('\n'))

    process = Popen(command, stdout=PIPE, stderr=STDOUT)
    with process.stdout:
        log_subprocess_output(process.stdout)
    return process.wait()
