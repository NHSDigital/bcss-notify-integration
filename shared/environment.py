# pylint: disable=duplicate-code
import json
import os
import requests

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


def seed():
    if os.getenv("SECRET_ARN") and not bool(os.getenv("ENVIRONMENT_SEEDED")):
        headers = {"X-Aws-Parameters-Secrets-Token": os.getenv('AWS_SESSION_TOKEN')}
        secrets_extension_endpoint = f"http://localhost:2773/secretsmanager/get?secretId={os.getenv('SECRET_ARN')}"
        r = requests.get(secrets_extension_endpoint, headers=headers, timeout=10)
        secrets = json.loads(r.text)["SecretString"]
        secrets_dict = json.loads(secrets)
        for key in KEYS:
            if key not in os.environ and key.lower() in secrets_dict:
                os.environ[key] = secrets_dict[key.lower()]
        os.environ["ENVIRONMENT_SEEDED"] = "true"
