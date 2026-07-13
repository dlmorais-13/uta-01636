import logging
import subprocess
import threading


def log_stream(stream, log_level, logger):
    """Reads a stream line by line and logs it."""
    for line in iter(stream.readline, b''):
        line_str = line.decode('latin1').strip()
        if line_str:
            logger.log(log_level, line_str)
    stream.close()


def exec(executable: str, args: list[str], workingDir, logger=logging.getLogger(__name__)):
    process = subprocess.Popen(
        [executable] + args,
        cwd=workingDir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    stdout_thread = threading.Thread(target=log_stream, args=(process.stdout, logging.INFO, logger))
    stderr_thread = threading.Thread(target=log_stream, args=(process.stderr, logging.ERROR, logger))
    stdout_thread.start()
    stderr_thread.start()
    stdout_thread.join()
    stderr_thread.join()
    return process.wait()
