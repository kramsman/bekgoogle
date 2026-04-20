"""Re-authenticate Application Default Credentials when gcloud auth expires."""

import subprocess
import google.auth
import google.auth.transport.requests


def ensure_adc_auth() -> None:
    """Check ADC credentials and trigger browser re-auth if expired."""
    try:
        creds, _ = google.auth.default()
        creds.refresh(google.auth.transport.requests.Request())
    except Exception as e:
        if not any(k in str(e).lower() for k in ("reauth", "expired", "invalid_grant", "could not be found", "credentials")):
            return
        print("\nGoogle credentials have expired. A browser window will open — sign in to continue.\n")
        subprocess.run(["gcloud", "auth", "application-default", "login"], check=True, start_new_session=True)
