# pylint: disable=duplicate-code
import json
import os
import requests
import time

KEYS = [
  "API_KEY",
  "APPLICATION_ID",
  "COMMGT_BASE_URL",
  "DATABASE_HOST",
  "DATABASE_PASSWORD",
  "DATABASE_PORT",
  "DATABASE_SID",
  "DATABASE_USER",
  "OAUTH_API_KEY",
  "OAUTH_API_KID",
  "OAUTH_TOKEN_URL",
  "PRIVATE_KEY"
]

class FetchSecretsError(BaseException):
    """Custom exception for fetch secrets errors."""


def seed():
    if os.getenv("SECRET_ARN") and not bool(os.getenv("ENVIRONMENT_SEEDED")):
        headers = {"X-Aws-Parameters-Secrets-Token": os.getenv('AWS_SESSION_TOKEN')}
        endpoint = f"http://localhost:2773/secretsmanager/get?secretId={os.getenv('SECRET_ARN')}&versionStage=AWSCURRENT"
        attempts = 0
        secrets = None

        while not secrets and attempts < 5:
            try:
                r = requests.get(endpoint, headers=headers, timeout=30)
                secrets = json.loads(r.text)["SecretString"]
            except requests.ConnectionError:
                attempts += 1
                time.sleep(attempts * 0.5)

        if not secrets:
            raise FetchSecretsError("Failed to retrieve secrets from AWS Secrets Manager")

        secrets_dict = json.loads(secrets)

        for key in KEYS:
            if key not in os.environ and key.lower() in secrets_dict:
                os.environ[key] = secrets_dict[key.lower()]
        os.environ["ENVIRONMENT_SEEDED"] = "true"
