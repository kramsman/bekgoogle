"""
write google secrets in manager from an .env file
from https://codelabs.developers.google.com/codelabs/secret-manager-python#5

the .env would be pairs of values, ex
  DATABASE_URL=postgres://user:password@localhost/mydb
  API_KEY=abc123xyz
  SECRET_TOKEN=s3cr3t_v@lue
  GOOGLE_PROJECT_ID=my-project-123
"""

from pathlib import Path

from dotenv import dotenv_values

from .get_creds import get_creds
from .google_secrets import (
    create_secret,
    delete_all_secrets,
    list_secrets,
)

ENV_DIR = "~/Downloads/"
SCOPES = ['https://www.googleapis.com/auth/cloud-platform']

PROJECT_ID = 'test-function-1'
PROJECT_NUM = '626996423295'


def upload_secrets():
    # read .env file into a dict named config
    config = dotenv_values(Path(ENV_DIR).expanduser() / ".env")

    # get token from credential json file
    creds = get_creds(scopes=SCOPES,
                      cred_file="client_secret_626996423295-29intjof3ek6lquo6pmv3tinlcef2s80.apps.googleusercontent.com.json",
                      cred_dir="/Users/Denise/Downloads",
                      write_token=False)
    token = creds.token

    print("Secrets before adding from dict")
    secret_list = list_secrets(token, PROJECT_NUM)
    print(secret_list, sep='\n')

    print("adding secrets")
    for key, val in config.items():
        create_secret(token, PROJECT_NUM, key, val)

    print("Secrets after adding from dict")
    secret_list = list_secrets(token, PROJECT_ID)
    print(secret_list, sep='\n')


if __name__ == '__main__':
    upload_secrets()
