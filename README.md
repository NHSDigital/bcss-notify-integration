# Bowel Cancer Screening System notifications

This repository contains a collection of serverless functions used to notify batches of recipients from the Bowel Cancer Screening System.

The functions are intended to be deployed to AWS Lambda.

## Functions

The names of the functions are a work in progress. They are described below:


### Batch Notification Processor

This function calls the BCSS Oracle database to obtain a batch of recipients eligible for pre-invitation notifications.
The function schedules a second function which performs a status check on notifications sent for the batch.


### Message Status Handler

This function checks the status of notification from the batch and is scheduled by the function.
This function is only scheduled if the batch processor function has successfully sent a batch to Communication Management API via the message batch endpoin.
It updates the status of a batch of pre-invitations in the BCSS Oracle database.
Currently the only status we update in Oracle is if the message has been read on the `nhsapp` channel within the last 24 hours.

## Development setup

### Prerequisites

- Python >= 3.11
- Docker (for local Oracle database)
- Docker compose plugin (for local Oracle database)

### Setup

Dependencies are managed using pipenv. To install the dependencies and activate the virtual environment, run:

```bash
pip install pipenv
pipenv install --dev
pipenv shell
```

### Environment variables

We use .env files to manage environment variables. To create a new .env file, copy the example file:

```bash
cp .env.example .env.local
```

### Oracle database container

We use a containerised Oracle database for local development and integration tests.
The development/test database connection details can be found in the .env.example file.
To start the Oracle database container, run:

```bash
./start-dev-environment.sh
```


## Linting

We use pylint for linting, this can be run using the script:

```bash
./lint.sh
```

## Running the tests

We use pytest for tests, these can be run using the script:

```bash
./test-unit.sh
```

## Accessing AWS Lambda Functions via the AWS Console

This section provides a high-level overview of how to access and work with AWS Lambda functions used by the project.  
It includes guidance on which accounts to use, how to navigate the AWS Console, and tips for safely finding the correct Lambda functions.

For the full step-by-step guide, see: [How to find AWS Lambdas in the AWS Console](docs/access-aws-lambdas.md)