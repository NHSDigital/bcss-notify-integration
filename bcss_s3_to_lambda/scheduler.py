import boto3
import json


class Scheduler:
    def __init__(self):
        self.scheduler = boto3.client("scheduler")
        self.flex_window = {"Mode": "OFF"}

    def schedule_batch_processor_retry(self, batch_id, schedule_expression):
        name = "lambda_batch_processor_retry"
        target = {
            "RoleArn": "<ROLE_ARN>",
            "Arn": "<LAMBDA_ARN>",
            "Input": self.payload(batch_id)
        }
        self.create_schedule(name, schedule_expression, target)

    def schedule_status_check(self, batch_id, schedule_expression):
        name = "lambda_status_check"
        target = {
            "RoleArn": "<ROLE_ARN>",
            "Arn": "<LAMBDA_ARN>",
            "Input": self.payload(batch_id)
        }
        self.create_schedule(name, schedule_expression, target)

    def create_schedule(self, name, schedule_expression, target):
        self.scheduler.create_schedule(
            Name=name,
            ScheduleExpression=schedule_expression,
            Target=target,
            FlexibleTimeWindow=self.flex_window)

    def payload(self, batch_id):
        return json.dumps({"batch_id": batch_id})
