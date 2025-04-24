# syntax=docker/dockerfile:1.4
FROM --platform=$BUILDPLATFORM python:3.13-bullseye AS builder

ENV API_KEY=${API_KEY} \
    APPLICATION_ID=${APPLICATION_ID} \
    COMMGT_BASE_URL=${COMMGT_BASE_URL} \
    DATABASE_USER=${DATABASE_USER} \
    DATABASE_PASSWORD=${DATABASE_PASSWORD} \ 
    DATABASE_SID=${DATABASE_SID} \
    DATABASE_HOST=${DATABASE_HOST} \
    DATABASE_PORT=${DATABASE_PORT} \
    OAUTH_API_KID=${OAUTH_API_KID} \
    OAUTH_API_KEY=${OAUTH_API_KEY} \
    OAUTH_TOKEN_URL=${OAUTH_TOKEN_URL} \
    PIP_ONLY_BINARY=ALL \
    PRIVATE_KEY=${PRIVATE_KEY} \
    REGION_NAME=${REGION_NAME} \
    SCHEDULE_STATUS_CHECK_MINUTES=${SCHEDULE_STATUS_CHECK_MINUTES}

COPY --from=root_dir .env.test /.env
COPY --from=root_dir message_status_handler/*.py /
COPY --from=root_dir Pipfile / 
COPY --from=root_dir Pipfile.lock /
COPY --from=root_dir shared/*.py /
COPY app.py /

RUN pip install pipenv flask dotenv
RUN pipenv install --system


ENTRYPOINT ["python3"]
CMD ["app.py"]
