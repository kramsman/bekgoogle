"""Append rows to a Google Sheet using the Sheets API v4."""


def append_to_sheet(sheet_service, spreadsheet_id: str, range_name: str,
                    values: list[list]) -> dict:
    """Append one or more rows to a Google Sheet.

    Rows are inserted after the last row of existing data in the given range.
    Uses the Sheets API v4 ``spreadsheets.values.append`` endpoint.

    Args:
        sheet_service: Authenticated Google Sheets API service object
            (from ``create_google_services()`` or ``googleapiclient.discovery.build()``).
        spreadsheet_id: The spreadsheet ID taken from the sheet URL
            (the long alphanumeric string between /d/ and /edit).
        range_name: Sheet tab and optional cell range, e.g. ``"Sheet1"`` or
            ``"Sheet1!A1"``. Only the tab name is needed when appending.
        values: List of rows to append. Each row is a list of cell values,
            e.g. ``[["Alice", "Smith", "alice@example.com"]]``.

    Returns:
        The API response dict (contains ``updates`` with metadata about what
        was written).

    Example::

        svc = create_google_services(scopes=[...])[1]   # sheet_service
        append_to_sheet(svc, "1BxiM...", "Sheet1", [["Alice", "Smith"]])
    """
    body = {"values": values}
    return (
        sheet_service.spreadsheets()
        .values()
        .append(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption="USER_ENTERED",
            insertDataOption="INSERT_ROWS",
            body=body,
        )
        .execute()
    )
