from unittest.mock import patch
from scheduler import Scheduler


@patch("boto3.client")
class TestScheduler:
    def test_schedule_batch_processor_retry(self, mock_boto3_scheduler):
        subject = Scheduler()
        subject.schedule_batch_processor_retry("123", "rate(5 minutes)")

        mock_boto3_scheduler.return_value.create_schedule.assert_called_once_with(
            Name="lambda_batch_processor_retry",
            ScheduleExpression="rate(5 minutes)",
            Target={
                "RoleArn": "<ROLE_ARN>",
                "Arn": "<LAMBDA_ARN>",
                "Input": '{"batch_id": "123"}'
            },
            FlexibleTimeWindow={"Mode": "OFF"}
        )

    def test_schedule_status_check(self, mock_boto3_scheduler):
        subject = Scheduler()
        subject.schedule_status_check("123", "rate(5 minutes)")

        mock_boto3_scheduler.return_value.create_schedule.assert_called_once_with(
            Name="lambda_status_check",
            ScheduleExpression="rate(5 minutes)",
            Target={
                "RoleArn": "<ROLE_ARN>",
                "Arn": "<LAMBDA_ARN>",
                "Input": '{"batch_id": "123"}'
            },
            FlexibleTimeWindow={"Mode": "OFF"}
        )

    def test_create_schedule(self, mock_boto3_scheduler):
        subject = Scheduler()
        subject.create_schedule(
            "name",
            "rate(5 minutes)",
            {"RoleArn": "role", "Arn": "arn", "Input": "input"},
        )

        mock_boto3_scheduler.return_value.create_schedule.assert_called_once_with(
            Name="name",
            ScheduleExpression="rate(5 minutes)",
            Target={"RoleArn": "role", "Arn": "arn", "Input": "input"},
            FlexibleTimeWindow={"Mode": "OFF"}
        )
