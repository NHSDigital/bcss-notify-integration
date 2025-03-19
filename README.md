# Bowel Cancer Screening System notifications

This repository contains a collection of serverless functions used to notify batches of recipients from the Bowel Cancer Screening System.

The functions are intended to be deployed to AWS Lambda.

## Functions

The names of the functions are a work in progress. They are described below:


### Batch processor

This function calls the BCSS Oracle database to obtain a batch of recipients eligible for pre-invitation notifications.
The function schedules a second function which performs a status check on notifications sent for the batch.


### Status checker

This function checks the status of notification from the batch and is scheduled by the function.
This function is only scheduled if the batch processor function has successfully sent a batch to Communication Management API via the message batch endpoin.
It updates the status of a batch of pre-invitations in the BCSS Oracle database.
Currently the only status we update in Oracle is if the message has been read on the `nhsapp` channel within the last 24 hours.


## Linting

We us pylint for linting, this can be run using the script:

```bash
./lint.sh
```

## Tests

We use pytest for tests, these can be run using the script:

```bash
./test-unit.sh
```
