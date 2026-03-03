"""Create and return authenticated Google Drive and Sheets API service objects."""

from pathlib import Path
from typing import Any

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from bekgoogle.get_creds import get_creds


def create_google_services(scopes: list[str], cred_dir: str | None = None) -> tuple[Any, Any]:
    """Create and return authenticated Google Drive and Sheets API service objects.

    Calls get_creds() with the supplied scopes. Credentials are read from
    cred_dir if provided, otherwise ~/.config/bekgoogle/ by default (or the
    GOOGLE_CREDS_DIR env var).

    Args:
        scopes: OAuth2 scopes to request, e.g. ['https://www.googleapis.com/auth/drive'].
        cred_dir: Directory containing credentials.json and token.json as a
            string (~ is expanded). Defaults to None (uses get_creds default).

    Returns:
        A (drive_service, sheet_service) tuple of authenticated API resources.
    """
    cred_path = Path(cred_dir).expanduser() if cred_dir is not None else None
    creds = get_creds(scopes=scopes, cred_dir=cred_path, token_dir=cred_path)
    try:
        drive_service = build('drive', 'v3', credentials=creds)
        sheet_service = build('sheets', 'v4', credentials=creds)
    except HttpError as err:
        print(err)

    return drive_service, sheet_service
