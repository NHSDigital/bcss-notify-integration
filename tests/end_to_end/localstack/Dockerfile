FROM --platform=$BUILDPLATFORM python:3.13-bullseye AS builder
RUN apt-get update && apt-get install -y zip

WORKDIR /dependencies

ENV PIPENV_VENV_IN_PROJECT=1

COPY --from=root_dir .env.test /.env
COPY --from=root_dir Pipfile /
COPY --from=root_dir Pipfile.lock /

RUN pip install pipenv
RUN pipenv install
RUN mkdir -p ./artefacts/
RUN cp -r $(pipenv --venv)/lib/python3.13/site-packages/* ./artefacts/

WORKDIR /dependencies/artefacts

RUN zip -r /batch_notification_processor.zip .
RUN zip -r /message_status_handler.zip .

WORKDIR /batch_notification_processor

COPY --from=root_dir .env.test /.env
COPY --from=root_dir batch_notification_processor/*.py /batch_notification_processor/
RUN zip -r /batch_notification_processor.zip /batch_notification_processor/*

WORKDIR /message_status_handler
COPY --from=root_dir .env.test /.env
COPY --from=root_dir message_status_handler/*.py /message_status_handler/
RUN zip -r /message_status_handler.zip /message_status_handler/*

WORKDIR /localstack

RUN pip install localstack awscli-local[ver1]

COPY --from=root_dir .env.test /.env
RUN awslocal lambda create-function \
      --function-name batch-notification-processor \
      --runtime python3.x \
      --zip-file fileb:///batch_notification_processor.zip \
      --handler lamdba_function.lambda_handler \
      --role arn:aws:iam::000000000000:role/lambda-role
