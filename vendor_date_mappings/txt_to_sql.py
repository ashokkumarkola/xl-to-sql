from pathlib import Path


# ==================================================
# Configuration
# ==================================================

INPUT_FILE = Path("Lido Mapping June 18 Unique.txt")
OUTPUT_FILE = Path("vendor_invoice_date_format_mappings.sql")

COLUMN_SEPARATOR = " | "

VENDOR_COLUMN_INDEX = 1
DATE_FORMAT_COLUMN_INDEX = 2

DEFAULT_DATE_FORMAT = "MM/DD/YYYY"

# ==================================================
# Exceptions
# ==================================================

class TxtToSqlError(Exception):
    """Base exception for TXT-to-SQL conversion errors."""


class InputFileError(TxtToSqlError):
    """Raised when the input TXT file is invalid or unavailable."""


class InvalidRowError(TxtToSqlError):
    """Raised when a TXT row does not contain required columns."""


# ==================================================
# Helpers
# ==================================================

def escape_sql(value: str) -> str:
    """
    Escape a string for use inside a PostgreSQL
    single-quoted string literal.
    """
    return value.replace("'", "''")


def build_insert_query(
    vendor_name: str,
    format_code: str,
) -> str:

    vendor_name = escape_sql(vendor_name)
    format_code = escape_sql(format_code)

    return f"""INSERT INTO vendor_invoice_date_format_mappings (
    vendor_id,
    date_format_id
)
SELECT
    v.id,
    f.id
FROM vendors v
CROSS JOIN invoice_date_formats f
WHERE v.vendor_name ILIKE '{vendor_name}'
  AND f.format_code ILIKE '{format_code}'
ON CONFLICT (vendor_id, date_format_id) DO NOTHING;
"""


# ==================================================
# TXT → SQL
# ==================================================

def txt_to_sql(
    input_file: Path,
    output_file: Path,
    column_separator: str = " | ",
    vendor_column_index: int = 1,
    date_format_column_index: int = 2,
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
    # Process rows
    # --------------------------------------------------

    queries: list[str] = []

    try:
        with input_file.open(
            "r",
            encoding="utf-8",
        ) as txt_file:

            for row_number, line in enumerate(
                txt_file,
                start=1,
            ):

                line = line.strip()

                # Skip empty lines
                if not line:
                    continue

                columns = [
                    column.strip()
                    for column in line.split(column_separator)
                ]

                required_columns = max(
                    vendor_column_index,
                    date_format_column_index,
                ) + 1

                if len(columns) <= vendor_column_index:
                    raise InvalidRowError(
                        f"Invalid row {row_number}: "
                        f"vendor name is missing.\n"
                        f"Row: {line}"
                    )

                vendor_name = columns[vendor_column_index]

                # Use default date format when missing
                if (
                    len(columns) <= date_format_column_index
                    or not columns[date_format_column_index]
                ):
                    format_code = DEFAULT_DATE_FORMAT
                else:
                    format_code = columns[date_format_column_index]

                if not vendor_name:
                    raise InvalidRowError(
                        f"Empty vendor name at row "
                        f"{row_number}."
                    )

                if not format_code:
                    raise InvalidRowError(
                        f"Empty date format at row "
                        f"{row_number}."
                    )

                queries.append(
                    build_insert_query(
                        vendor_name=vendor_name,
                        format_code=format_code,
                    )
                )

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
    # Write SQL
    # --------------------------------------------------

    try:
        with output_file.open(
            "w",
            encoding="utf-8",
        ) as sql_file:

            for query in queries:
                sql_file.write(query)
                sql_file.write("\n")

    except PermissionError as exc:
        raise TxtToSqlError(
            f"Permission denied while writing "
            f"'{output_file}'."
        ) from exc

    except OSError as exc:
        raise TxtToSqlError(
            f"Unable to write '{output_file}': {exc}"
        ) from exc

    # --------------------------------------------------
    # Result
    # --------------------------------------------------

    print(
        "Conversion successful.\n"
        f"Input : {input_file}\n"
        f"Output: {output_file}\n"
        f"Queries generated: {len(queries)}"
    )


# ==================================================
# Main
# ==================================================

if __name__ == "__main__":

    try:

        txt_to_sql(
            input_file=INPUT_FILE,
            output_file=OUTPUT_FILE,
            column_separator=COLUMN_SEPARATOR,
            vendor_column_index=VENDOR_COLUMN_INDEX,
            date_format_column_index=DATE_FORMAT_COLUMN_INDEX,
        )

    except TxtToSqlError as exc:

        print(f"\nERROR: {exc}\n")

    except KeyboardInterrupt:

        print("\nERROR: Operation cancelled by user.")

    except Exception as exc:

        print(
            f"\nUNEXPECTED ERROR: "
            f"{type(exc).__name__}: {exc}\n"
        )

        raise