from pathlib import Path


# ==================================================
# Configuration
# ==================================================

INPUT_FILE = Path("Lido Mapping June 18.txt")
OUTPUT_FILE = Path("Lido Mapping June 18 Unique.txt")

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

    unique_records: set[str] = set()
    total_records = 0
    duplicate_records = 0

    try:
        with input_file.open(
            "r",
            encoding="utf-8",
        ) as txt_file:

            for line in txt_file:

                record = line.strip()

                if skip_empty_lines and not record:
                    continue

                total_records += 1

                if record in unique_records:
                    duplicate_records += 1
                    continue

                unique_records.add(record)

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

    print(
        "Processing successful.\n"
        f"Input             : {input_file}\n"
        f"Output            : {output_file}\n"
        f"Total records     : {total_records}\n"
        f"Unique records    : {len(unique_records)}\n"
        f"Duplicate records : {duplicate_records}"
    )


# ==================================================
# Main
# ==================================================

if __name__ == "__main__":

    try:

        remove_duplicates(
            input_file=INPUT_FILE,
            output_file=OUTPUT_FILE,
            skip_empty_lines=SKIP_EMPTY_LINES,
        )

    except UniqueTxtError as exc:

        print(f"\nERROR: {exc}\n")

    except KeyboardInterrupt:

        print("\nERROR: Operation cancelled by user.")

    except Exception as exc:

        print(
            f"\nUNEXPECTED ERROR: "
            f"{type(exc).__name__}: {exc}\n"
        )

        raise