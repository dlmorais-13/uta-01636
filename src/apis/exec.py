"""
File with functions to wrap binary execution with logic
that checks output for success messages, using predefined string 
pattern, and wraps the outputs (out and err) into the regular 
logging mechanism.
"""

import logging
import subprocess
import threading


def log_stream(stream, log_level, logger, list_to_save: list[str] = None):
    """
    Reads a stream line by line and logs it, optionally saving output to a list.

    Args:
        stream: The stream to read.
        log_level: The log level to use in the log.
        logger: The instance of the logger to use.
        list_to_save: List to save the output into.
            Optional. Default to none.
    """

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
    working_dir: str,
    expected_output: str = None,
    logger=logging.getLogger(__name__),
):
    """
    Executes a binary, with given arguments, in a given working directory,
    optionally checking the output for success messages.

    Args:
        executable: The full path to the executable file.
        args: The list of arguments to pass to the executable.
        workingDir: The folder to execute the binary from.
        expectec_output: A string that should be in the output for
            the command to be considered successful.
            Optional. Defaults to none.
        logger: The logger instance to use. Optional. Defaults
            to a newly created logger.

    Returns:
        The exit status of the executed command.
    """
    
    process = subprocess.Popen(
        [executable] + args,
        cwd=working_dir,
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
