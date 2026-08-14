from pathlib import Path
from openpyxl import load_workbook
from openpyxl.utils.exceptions import InvalidFileException


# ==================================================
# Exceptions
# ==================================================

class ExcelToTxtError(Exception):
    """Base exception for Excel-to-TXT conversion errors."""


class InputFileError(ExcelToTxtError):
    """Raised when the input Excel file is invalid or unavailable."""


class SheetNotFoundError(ExcelToTxtError):
    """Raised when the requested worksheet does not exist."""


class ColumnNotFoundError(ExcelToTxtError):
    """Raised when a required column does not exist."""


class DataConversionError(ExcelToTxtError):
    """Raised when Excel data cannot be converted."""


# ==================================================
# Configuration
# ==================================================

INPUT_FILE = Path("data/Lido Mapping June 18.xlsx")
OUTPUT_FILE = Path("Lido Mapping June 18.txt")

SHEET_NAME = "in"

INCLUDE_HEADER = False

SELECTED_COLUMNS = [
    # "Invoice - Vendor",
    "NextGen - Vendor",
    "Invoice - Date Format",
]

COLUMN_SEPARATOR = " | "

SKIP_EMPTY_ROWS = True

# ==================================================
# Excel - TXT
# ==================================================

def excel_to_txt(
    input_file: Path,
    output_file: Path,
    sheet_name: str,
    selected_columns: list[str],
    include_header: bool = False,
    column_separator: str = " | ",
    skip_empty_rows: bool = True,
) -> None:

    # --------------------------------------------------
    # Validate input file
    # --------------------------------------------------

    if not input_file.exists():
        raise InputFileError(
            f"Input Excel file not found: '{input_file}'"
        )

    if not input_file.is_file():
        raise InputFileError(
            f"Input path is not a file: '{input_file}'"
        )

    if input_file.suffix.lower() not in {".xlsx", ".xlsm"}:
        raise InputFileError(
            f"Unsupported Excel file type: '{input_file.suffix}'. "
            f"Expected .xlsx or .xlsm."
        )

    # --------------------------------------------------
    # Load workbook
    # --------------------------------------------------

    try:
        workbook = load_workbook(
            input_file,
            data_only=True,
        )
    except InvalidFileException as exc:
        raise InputFileError(
            f"Unable to read Excel file '{input_file}'. "
            f"The file may be corrupted or invalid."
        ) from exc
    except PermissionError as exc:
        raise InputFileError(
            f"Permission denied while reading Excel file "
            f"'{input_file}'."
        ) from exc
    except OSError as exc:
        raise InputFileError(
            f"Unable to open Excel file '{input_file}': {exc}"
        ) from exc

    # --------------------------------------------------
    # Validate sheet
    # --------------------------------------------------

    if sheet_name not in workbook.sheetnames:
        available_sheets = ", ".join(
            f"'{name}'" for name in workbook.sheetnames
        )

        raise SheetNotFoundError(
            f"Worksheet '{sheet_name}' was not found in "
            f"'{input_file.name}'.\n"
            f"Available worksheets: {available_sheets}\n"
            f"Please update SHEET_NAME in the configuration."
        )

    sheet = workbook[sheet_name]

    # --------------------------------------------------
    # Validate worksheet
    # --------------------------------------------------

    if sheet.max_row < 1:
        raise ExcelToTxtError(
            f"Worksheet '{sheet_name}' is empty. "
            f"Expected the first row to contain column headers."
        )

    # --------------------------------------------------
    # Read headers
    # --------------------------------------------------

    headers = [
        str(cell.value).strip()
        if cell.value is not None
        else ""
        for cell in sheet[1]
    ]

    if not any(headers):
        raise ExcelToTxtError(
            f"Worksheet '{sheet_name}' does not contain "
            f"any column headers in the first row."
        )

    # --------------------------------------------------
    # Validate selected columns
    # --------------------------------------------------

    column_indexes: dict[str, int] = {}

    for column_name in selected_columns:

        if column_name not in headers:
            available_columns = ", ".join(
                f"'{column}'"
                for column in headers
                if column
            )

            raise ColumnNotFoundError(
                f"Required column '{column_name}' was not found "
                f"in worksheet '{sheet_name}'.\n"
                f"Available columns: {available_columns}\n"
                f"Please check SELECTED_COLUMNS."
            )

        column_indexes[column_name] = headers.index(column_name)

    # --------------------------------------------------
    # Validate output directory
    # --------------------------------------------------

    output_directory = output_file.parent

    if not output_directory.exists():
        raise ExcelToTxtError(
            f"Output directory does not exist: "
            f"'{output_directory}'"
        )

    # --------------------------------------------------
    # Write TXT
    # --------------------------------------------------

    try:
        with output_file.open(
            "w",
            encoding="utf-8",
        ) as txt_file:

            # Header
            if include_header:
                txt_file.write(
                    column_separator.join(selected_columns)
                    + "\n"
                )

            # Data
            print(f"Reading rows from sheet '{sheet_name}'...")

            total_rows = 0
            written_rows = 0
            empty_rows = 0

            for row_number, row in enumerate(
                sheet.iter_rows(
                    min_row=2,
                    values_only=True,
                ),
                start=2,
            ):

                total_rows += 1

                values = []

                for column_name in selected_columns:

                    column_index = column_indexes[column_name]

                    try:
                        value = row[column_index]
                    except IndexError as exc:
                        raise DataConversionError(
                            f"Unable to read column "
                            f"'{column_name}' at Excel row "
                            f"{row_number}."
                        ) from exc

                    values.append(
                        "" if value is None else str(value).strip()
                    )

                if not any(values):
                    empty_rows += 1

                    if skip_empty_rows:
                        print(f"  [SKIP]  Row {row_number}: empty, skipped.")
                        continue

                    print(f"  [EMPTY] Row {row_number}: empty, kept.")

                written_rows += 1
                print(
                    f"  [OK]    Row {row_number}: "
                    f"{column_separator.join(values)}"
                )

                txt_file.write(
                    column_separator.join(values)
                    + "\n"
                )

    except PermissionError as exc:
        raise ExcelToTxtError(
            f"Permission denied while writing output file "
            f"'{output_file}'."
        ) from exc

    except OSError as exc:
        raise ExcelToTxtError(
            f"Unable to write output file "
            f"'{output_file}': {exc}"
        ) from exc

    finally:
        workbook.close()

    print(
        f"\nConversion successful.\n"
        f"Input       : {input_file}\n"
        f"Sheet       : {sheet_name}\n"
        f"Output      : {output_file}\n"
        f"Rows scanned: {total_rows}\n"
        f"Rows written: {written_rows}\n"
        f"Empty rows  : {empty_rows}"
        f"{' (skipped)' if skip_empty_rows else ' (kept)'}"
    )


# ==================================================
# Main
# ==================================================

if __name__ == "__main__":

    try:
        excel_to_txt(
            input_file=INPUT_FILE,
            output_file=OUTPUT_FILE,
            sheet_name=SHEET_NAME,
            selected_columns=SELECTED_COLUMNS,
            include_header=INCLUDE_HEADER,
            column_separator=COLUMN_SEPARATOR,
            skip_empty_rows=SKIP_EMPTY_ROWS,
        )

    except ExcelToTxtError as exc:
        print(f"\nERROR: {exc}\n")

    except KeyboardInterrupt:
        print("\nERROR: Operation cancelled by user.")

    except Exception as exc:
        print(
            f"\nUNEXPECTED ERROR: "
            f"{type(exc).__name__}: {exc}\n"
        )
        raise