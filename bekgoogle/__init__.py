"""Google Drive and Sheets API helpers, resolved lazily.

Names are looked up on first use rather than imported here. Importing eagerly
meant `from bekgoogle import ensure_adc_auth` — wanted by any script that reads a
secret — also pulled in the Drive/Sheets modules, and through them uvbekutils and
PySide6. That turns a plain terminal script into a macOS GUI app which takes a
dock icon and steals keyboard focus from its own prompts.

It also made every import pay for googleapiclient and pandas whether or not the
caller touched Drive or Sheets.

Usage is unchanged:

    from bekgoogle import ensure_adc_auth, get_secret     # still works
    from bekgoogle.ensure_adc import ensure_adc_auth      # still works
"""

import importlib

# public name -> submodule that defines it
_LAZY = {
    "ensure_adc_auth":                    "ensure_adc",
    "get_creds":                          "get_creds",
    "get_serviceaccount_creds":           "get_serviceaccount_creds",

    "get_secret":                         "google_secrets",
    "create_secret":                      "google_secrets",
    "create_secret_only":                 "google_secrets",
    "delete_all_secrets":                 "google_secrets",
    "delete_secret":                      "google_secrets",
    "list_secret_info":                   "google_secrets",
    "list_secret_versions":               "google_secrets",
    "list_secrets":                       "google_secrets",
    "update_secret":                      "google_secrets",
    "upload_secrets":                     "upload_secrets",

    "get_sheet_values":                   "get_sheet_values",
    "append_to_sheet":                    "append_to_sheet",
    "upload_sheet_to_drive":              "upload_sheet_to_drive",
    "permission_to_drive_file":           "permission_to_drive_file",
    "get_google_file_or_folder_ids":      "get_google_file_or_folder_ids",
    "delete_list_of_google_files":        "delete_list_of_google_files",
    "create_drive_subfolder":             "create_drive_subfolder",
    "create_google_services":             "create_google_services",
    "create_google_services_serviceaccount": "create_google_services_serviceaccount",
}

__all__ = sorted(_LAZY)


def __getattr__(name):
    """PEP 562 — resolve a public name to its submodule on first access."""
    if name in _LAZY:
        value = getattr(importlib.import_module(f".{_LAZY[name]}", __name__), name)
        globals()[name] = value          # cache so this runs once per name
        return value
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__():
    return __all__
