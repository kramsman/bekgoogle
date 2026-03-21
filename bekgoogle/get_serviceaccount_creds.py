"""Return Google service account credentials from a key file."""
from pathlib import Path

from google.oauth2 import service_account


def get_serviceaccount_creds(service_account_file: str | Path, scopes: list[str]):
    """Return service account Credentials for the given key file and scopes."""
    return service_account.Credentials.from_service_account_file(
        str(service_account_file), scopes=scopes
    )
