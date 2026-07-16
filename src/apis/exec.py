import logging
import subprocess
import threading


def log_stream(stream, log_level, logger, list_to_save: list[str] = None):
    """Reads a stream line by line and logs it."""
    for line in iter(stream.readline, b""):
        line_str = line.decode("latin1").strip()
        if line_str:
            logger.log(log_level, line_str)
            if list_to_save is not None:
                list_to_save.append(line_str)
    stream.close()


def exec(
    executable: str,
    args: list[str],
    workingDir,
    expected_output: str = None,
    logger=logging.getLogger(__name__),
):
    process = subprocess.Popen(
        [executable] + args,
        cwd=workingDir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    stdout_content = None
    if expected_output is not None:
        stdout_content = []

    stdout_thread = threading.Thread(
        target=log_stream, args=(process.stdout, logging.INFO, logger, stdout_content)
    )
    stderr_thread = threading.Thread(
        target=log_stream, args=(process.stderr, logging.ERROR, logger)
    )
    stdout_thread.start()
    stderr_thread.start()
    stdout_thread.join()
    stderr_thread.join()
    status = process.wait()

    cmd = " ".join([executable] + args)
    if status != 0:
        logger.error(f"Error on command execution: Command: {cmd} | Status {status}.")
    elif expected_output is not None:
        match = next((line for line in stdout_content if expected_output in line), None)
        if match is None:
            raise Exception(
                f'Expected output "{expected_output}" not found in "{cmd}" output.'
            )

    return status
