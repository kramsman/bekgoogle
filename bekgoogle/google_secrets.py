"""Google Secret Manager helpers using the REST API and the client library."""

import base64

import requests
from google.cloud import secretmanager
from loguru import logger


_secret_cache: dict[tuple[str, str], str] = {}
_client_cache: dict[str, secretmanager.SecretManagerServiceClient] = {}


def get_secret(secret_id: str, project_id: str, use_cache: bool = True) -> str:
    """Read the latest version of a secret's value.

    The counterpart to the create/update/delete helpers here, which had no way to
    read a value back — so every caller hand-wrote this, and the copies drifted.

    Retries once through ``ensure_adc_auth`` when Application Default Credentials
    have expired, which is the common failure on a workstation. That import is
    deliberately local: importing it at module level would pull in the Drive and
    Sheets helpers, and through them PySide6.

    Args:
        secret_id: Name of the secret, e.g. "PCP_APP_ID".
        project_id: Google Cloud project id holding the secret.
        use_cache: Reuse a value already read in this process. Set False when a
            secret may have been rotated during the run.

    Returns:
        The secret's latest value, decoded as UTF-8.

    Raises:
        Exception: Whatever Secret Manager raised, if it was not an expired-ADC
            error or the retry also failed.
    """
    key = (project_id, secret_id)
    if use_cache and key in _secret_cache:
        return _secret_cache[key]

    name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"

    def _read(client):
        return client.access_secret_version(request={"name": name}).payload.data.decode("UTF-8")

    client = _client_cache.get(project_id) or secretmanager.SecretManagerServiceClient()
    _client_cache[project_id] = client
    try:
        value = _read(client)
    except Exception as e:
        if "Reauthentication is needed" not in str(e):
            raise
        from bekgoogle.ensure_adc import ensure_adc_auth
        ensure_adc_auth()
        client = secretmanager.SecretManagerServiceClient()
        _client_cache[project_id] = client
        value = _read(client)

    _secret_cache[key] = value
    return value


def create_secret_only(token: str, project_num: str, secret_id: str) -> tuple[bool, int]:
    """Creates a secret container in Google Secret Manager without a value.

    Args:
        token: OAuth2 bearer token for authentication.
        project_num: Google Cloud project number.
        secret_id: Identifier for the new secret.

    Returns:
        A tuple of (success flag, HTTP status code).
    """
    headers = eval(f"{{'Content-Type': 'application/json', 'Authorization': 'Bearer  {token}'}}")
    url = f"https://secretmanager.googleapis.com/v1/projects/{project_num}/secrets/"
    r = requests.post(url, headers=headers, params={"secret_id": secret_id},
                      json={"replication": {"automatic": {}}}, timeout=5)
    logger.debug(f"({r.content=}, {r.status_code=}, {r.ok=}, {r.text=}")
    print(f"({r.content=}, {r.status_code=}, {r.ok=}, {r.text=}")
    return r.ok, r.status_code


def create_secret(token: str, project_num: str, secret_id: str, value: str) -> None:
    """Creates a secret in Google Secret Manager with an initial value.

    Deletes any existing secret with the same ID, creates a new one,
    then populates it with the provided value.

    Args:
        token: OAuth2 bearer token for authentication.
        project_num: Google Cloud project number.
        secret_id: Identifier for the secret.
        value: The secret value to store.
    """
    headers = eval(f"{{'Content-Type': 'application/json', 'Authorization': 'Bearer  {token}'}}")
    delete_secret(token, project_num, secret_id)
    ok, status_code = create_secret_only(token, project_num, secret_id)
    if ok:
        base64_string = base64.b64encode(value.encode("ascii")).decode("ascii")
        url = f"https://secretmanager.googleapis.com/v1/projects/{project_num}/secrets/{secret_id}:addVersion"
        r = requests.post(url, headers=headers, json={'payload': {'data': base64_string}}, timeout=5)
        logger.debug(f"({r.content=}, {r.status_code=}, {r.ok=}, {r.text=}")
        print(f"({r.content=}, {r.status_code=}, {r.ok=}, {r.text=}")


def list_secrets(token: str, project_num: str) -> list[str] | None:
    """Lists all secret names in the given Google Cloud project.

    Args:
        token: OAuth2 bearer token for authentication.
        project_num: Google Cloud project number.

    Returns:
        List of secret name strings, or None if no secrets found.
    """
    url = f"https://secretmanager.googleapis.com/v1/projects/{project_num}/secrets/"
    headers = eval(f"{{'Content-Type': 'application/json', 'Authorization': 'Bearer  {token}'}}")
    r = requests.get(url, headers=headers, timeout=5)
    logger.debug(f"({r.content=}, {r.status_code=}, {r.ok=}, {r.text=}")
    print(f"{r.status_code=}, {r.ok=}, {r.reason=}, {r.text=}")
    if r.json():
        return [secret['name'].split('/')[-1] for secret in r.json()['secrets']]
    return None


def update_secret(client: secretmanager.SecretManagerServiceClient,
                  project_id: str, secret_id: str) -> secretmanager.UpdateSecretRequest:
    """Updates the metadata about an existing secret.

    Args:
        client: Authenticated Secret Manager client.
        project_id: Google Cloud project ID.
        secret_id: Identifier of the secret to update.

    Returns:
        The update response from the Secret Manager API.
    """
    name = client.secret_path(project_id, secret_id)
    secret = {"name": name, "labels": {"secretmanager": "rocks"}}
    update_mask = {"paths": ["labels"]}
    response = client.update_secret(request={"secret": secret, "update_mask": update_mask})
    logger.debug(f"Updated secret: {response.name}")
    print(f"Updated secret: {response.name}")


def delete_secret(token: str, project_num: str, secret_id: str) -> None:
    """Deletes the secret with the given name and all of its versions.

    Args:
        token: OAuth2 bearer token for authentication.
        project_num: Google Cloud project number.
        secret_id: Identifier of the secret to delete.
    """
    url = f"https://secretmanager.googleapis.com/v1/projects/{project_num}/secrets/{secret_id}"
    headers = eval(f"{{'Content-Type': 'application/json', 'Authorization': 'Bearer  {token}'}}")
    r = requests.delete(url, headers=headers, timeout=5)
    logger.debug(f"({r.content=}, {r.status_code=}, {r.ok=}, {r.text=}")
    print(f"{r.status_code=}, {r.ok=}, {r.reason=}, {r.text=}")


def delete_all_secrets(token: str, project_num: str) -> None:
    """Deletes all secrets in a project.

    Args:
        token: OAuth2 bearer token for authentication.
        project_num: Google Cloud project number.
    """
    for secret in list_secrets(token, project_num):
        delete_secret(token, project_num, secret)


def list_secret_info(token: str, project_id: str, secret_id: str) -> None:
    """Prints metadata for a specific secret.

    Args:
        token: OAuth2 bearer token for authentication.
        project_id: Google Cloud project ID.
        secret_id: Identifier of the secret to inspect.
    """
    url = f"https://secretmanager.googleapis.com/v1/projects/{project_id}/secrets/{secret_id}"
    headers = eval(f"{{'Content-Type': 'application/json', 'Authorization': 'Bearer  {token}'}}")
    r = requests.get(url, headers=headers, timeout=5)
    print(f"{r.ok=}, {r.status_code=}, {r.reason=}, {r.text=}")


def list_secret_versions(project_id: str, secret_id: str) -> None:
    """Lists all secret versions in the given secret and their metadata.

    Args:
        project_id: Google Cloud project ID.
        secret_id: Identifier of the secret whose versions to list.
    """
    client = secretmanager.SecretManagerServiceClient()
    parent = f"projects/{project_id}"
    for version in client.list_secret_versions(request={"parent": parent}):
        logger.debug(f"Found secret version: {version.name}")
        print(f"Found secret version: {version.name}")
