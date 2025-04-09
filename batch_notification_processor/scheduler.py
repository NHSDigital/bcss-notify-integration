import datetime
import json
import logging
import os
import boto3


class Scheduler:
    MAX_RETRIES = 5
    SCHEDULE_FORMAT = "at(%Y-%m-%dT%H:%M:%S)"

    def __init__(self, batch_id: str, retries: int = 0):
        self.batch_id = batch_id
        self.retries = retries + 1
        self.scheduler = boto3.client("scheduler")
        self.flex_window = {"Mode": "OFF"}

    def schedule_batch_processor_retry(self, minutes_from_now: int):
        name = "lambda_batch_processor_retry"
        target = {
            "RoleArn": os.getenv("LAMBDA_BATCH_PROCESSOR_ROLE_ARN"),
            "Arn": os.getenv("LAMBDA_BATCH_PROCESSOR_ARN"),
            "Input": self.payload()
        }
        logging.info(
            "Scheduling batch processor retry. batch_id: %s, retries: %s",
            self.batch_id, self.retries
        )
        self.create_schedule(name, minutes_from_now, target)

    def schedule_status_check(self, minutes_from_now: int):
        name = "lambda_status_check"
        target = {
            "RoleArn": os.getenv("LAMBDA_STATUS_CHECK_ROLE_ARN"),
            "Arn": os.getenv("LAMBDA_STATUS_CHECK_ARN"),
            "Input": self.payload()
        }

        logging.info(
            "Scheduling status check. batch_id: %s, retries: %s",
            self.batch_id, self.retries
        )
        if minutes_from_now == 0:
            self.invoke_immediately()
        else:
            self.create_schedule(name, minutes_from_now, target)

    def create_schedule(self, name: str, minutes_from_now: int, target: dict):
        if self.retries > self.MAX_RETRIES:
            return

        scheduled_at = Scheduler.schedule_time(minutes_from_now)

        self.scheduler.create_schedule(
            Name=name,
            ScheduleExpression=scheduled_at.strftime(self.SCHEDULE_FORMAT),
            Target=target,
            FlexibleTimeWindow=self.flex_window)

    def payload(self):
        return json.dumps({"batch_id": self.batch_id, "retries": self.retries})

    def invoke_immediately(self):
        boto3.client("lambda").invoke(
            FunctionName=os.getenv("LAMBDA_BATCH_PROCESSOR_ARN"),
            InvocationType="Event",
            Payload=self.payload()
        )

    @staticmethod
    def schedule_time(minutes_from_now: int):
        return Scheduler.now() + datetime.timedelta(minutes=minutes_from_now)

    @staticmethod
    def now():
        return datetime.datetime.now()
