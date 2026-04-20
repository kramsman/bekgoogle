"""Re-authenticate Application Default Credentials when gcloud auth expires."""

import subprocess
from uvbekutils import pyautobek


def ensure_adc_auth() -> None:
    """Open browser re-auth when gcloud ADC credentials have expired."""
    pyautobek.alert(
        "Google credentials have expired.\n\n"
        "A browser window will open — sign in with your Google account to continue.",
        "Re-authenticate Google",
    )
    subprocess.run(["gcloud", "auth", "application-default", "login"], check=True)
