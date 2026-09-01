import logging
import os
import sys
import re


class RelativeSeconds(logging.Formatter):
    def format(self, record):
        # Convert milliseconds to seconds (float)
        record.relativeCreated = record.relativeCreated / 1000.0
        # Call the parent class's format method
        return super().format(record)


class FileFormatter(RelativeSeconds):
    # Regex to match ANSI escape sequences
    _ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

    def format(self, record):
        original_message = super().format(record)
        return self._ansi_escape.sub("", original_message)


format_str = "%(asctime)s - %(threadName)s - %(relativeCreated)fs - %(levelname)s - %(name)s - %(message)s"

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(RelativeSeconds(format_str))

# Configure the logging
if "LOG_FILE" in os.environ:
    file_handler = logging.FileHandler("workdir/app.log", mode="a", encoding="utf-8")
    file_handler.setFormatter(FileFormatter(format_str))

    logging.basicConfig(
        level=logging.INFO,
        handlers=[stream_handler, file_handler],
    )
else:
    # logging.basicConfig(level=logging.DEBUG if settings.debug else logging.INFO)
    logging.basicConfig(level=logging.INFO, handlers=[stream_handler])

# Limit memory usage
if "MEM_LIMIT" in os.environ:
    mem_limit_mb = int(os.environ["MEM_LIMIT"])
    mem_limit_bytes = mem_limit_mb * 1024 * 1024
    import resource

    soft, hard = resource.getrlimit(resource.RLIMIT_AS)
    resource.setrlimit(resource.RLIMIT_AS, (mem_limit_bytes, hard))

# import arcgis
# arcgis.env.verbose = True
