"""Shared logging setup: clean per-row logs to a file, summary/errors to console."""

import logging
from datetime import datetime
from pathlib import Path

LOG_DIR = Path("logs")


def setup_logging(
    script_name: str,
    log_dir: Path = LOG_DIR,
) -> tuple[logging.Logger, logging.Logger]:
    """
    Configure logging for a script.

    Creates a timestamped log file under `log_dir` for per-row detail
    logs, and a console-only logger for summaries and errors.

    Returns:
        console_logger: logs summary/error messages to the console.
        row_logger: writes clean, per-row detail logs to the log file.
    """

    log_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"{script_name}_{timestamp}.log"

    console_logger = logging.getLogger(f"{script_name}.console")
    console_logger.setLevel(logging.INFO)
    console_logger.propagate = False

    if not console_logger.handlers:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter("%(message)s"))
        console_logger.addHandler(console_handler)

    row_logger = logging.getLogger(f"{script_name}.rows")
    row_logger.setLevel(logging.INFO)
    row_logger.propagate = False

    if not row_logger.handlers:
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(logging.Formatter("%(message)s"))
        row_logger.addHandler(file_handler)

    return console_logger, row_logger
