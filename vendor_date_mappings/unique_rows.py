import logging
from pathlib import Path

from logging_utils import setup_logging

SCRIPT_NAME = "unique_rows"

logger: logging.Logger
row_logger: logging.Logger


# ==================================================
# Configuration
# ==================================================

INPUT_FILE = Path("./txt_files/Lido Mapping June 18.txt")
OUTPUT_FILE = Path("./txt_files/Lido Mapping June 18 Unique.txt")

SKIP_EMPTY_LINES = True


# ==================================================
# Exceptions
# ==================================================

class UniqueTxtError(Exception):
    """Base exception for TXT unique-record processing errors."""


class InputFileError(UniqueTxtError):
    """Raised when the input TXT file is invalid or unavailable."""


class OutputFileError(UniqueTxtError):
    """Raised when the output TXT file cannot be written."""


# ==================================================
# TXT - Unique Records
# ==================================================

def remove_duplicates(
    input_file: Path,
    output_file: Path,
    skip_empty_lines: bool = True,
) -> None:

    # --------------------------------------------------
    # Validate input
    # --------------------------------------------------

    if not input_file.exists():
        raise InputFileError(
            f"Input TXT file not found: '{input_file}'"
        )

    if not input_file.is_file():
        raise InputFileError(
            f"Input path is not a file: '{input_file}'"
        )

    # --------------------------------------------------
    # Read and process
    # --------------------------------------------------

    unique_records: dict[str, None] = {}
    total_records = 0
    duplicate_records = 0

    logger.info("Reading rows from '%s'...", input_file)

    try:
        with input_file.open(
            "r",
            encoding="utf-8",
        ) as txt_file:

            for row_number, line in enumerate(
                txt_file,
                start=1,
            ):

                record = line.strip()

                if skip_empty_lines and not record:
                    row_logger.info("  [SKIP]  Row %d: empty, skipped.", row_number)
                    continue

                total_records += 1

                if record in unique_records:
                    duplicate_records += 1
                    row_logger.info("  [DUP]   Row %d: %s", row_number, record)
                    continue

                unique_records[record] = None
                row_logger.info("  [OK]    Row %d: %s", row_number, record)

    except PermissionError as exc:
        raise InputFileError(
            f"Permission denied while reading "
            f"'{input_file}'."
        ) from exc

    except OSError as exc:
        raise InputFileError(
            f"Unable to read '{input_file}': {exc}"
        ) from exc

    # --------------------------------------------------
    # Write unique records
    # --------------------------------------------------

    try:
        with output_file.open(
            "w",
            encoding="utf-8",
        ) as txt_file:

            for record in unique_records:
                txt_file.write(record + "\n")

    except PermissionError as exc:
        raise OutputFileError(
            f"Permission denied while writing "
            f"'{output_file}'."
        ) from exc

    except OSError as exc:
        raise OutputFileError(
            f"Unable to write '{output_file}': {exc}"
        ) from exc

    # --------------------------------------------------
    # Result
    # --------------------------------------------------

    logger.info(
        "\nProcessing successful.\n"
        "Input             : %s\n"
        "Output            : %s\n"
        "Total records     : %d\n"
        "Unique records    : %d\n"
        "Duplicate records : %d",
        input_file,
        output_file,
        total_records,
        len(unique_records),
        duplicate_records,
    )


# ==================================================
# Main
# ==================================================

def configure_logging() -> None:
    """Configure console (summary/errors) and file (per-row) loggers."""

    global logger, row_logger
    logger, row_logger = setup_logging(SCRIPT_NAME)


def main() -> None:
    configure_logging()

    try:
        remove_duplicates(
            input_file=INPUT_FILE,
            output_file=OUTPUT_FILE,
            skip_empty_lines=SKIP_EMPTY_LINES,
        )

    except UniqueTxtError as exc:
        logger.error("\nERROR: %s\n", exc)

    except KeyboardInterrupt:
        logger.error("\nERROR: Operation cancelled by user.")

    except Exception:
        logger.exception("\nUNEXPECTED ERROR:")
        raise


if __name__ == "__main__":
    main()
