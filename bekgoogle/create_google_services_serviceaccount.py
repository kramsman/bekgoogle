"""Create Google Drive and Sheets services using a service account key file."""
from pathlib import Path
from typing import Any

from googleapiclient.discovery import build

from bekgoogle.get_serviceaccount_creds import get_serviceaccount_creds


def create_google_services_serviceaccount(
    service_account_file: str | Path, scopes: list[str]
) -> tuple[Any, Any]:
    """Return (drive_service, sheet_service) authenticated via a service account key file.

    Args:
        service_account_file: Path to the service account JSON key file.
        scopes: List of OAuth scopes required (e.g. ['https://www.googleapis.com/auth/drive']).

    Returns:
        Tuple of (drive_service, sheet_service) API resource objects.
    """
    creds = get_serviceaccount_creds(service_account_file, scopes)
    drive_service = build("drive", "v3", credentials=creds)
    sheet_service = build("sheets", "v4", credentials=creds)
    return drive_service, sheet_service
