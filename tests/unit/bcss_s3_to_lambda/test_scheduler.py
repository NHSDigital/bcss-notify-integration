import datetime
import os
from unittest.mock import patch, Mock
from scheduler import Scheduler

mock_arns = {
    "LAMBDA_BATCH_PROCESSOR_ROLE_ARN": "<BATCH_PROCESSOR_ROLE_ARN>",
    "LAMBDA_BATCH_PROCESSOR_ARN": "<BATCH_PROCESSOR_LAMBDA_ARN>",
    "LAMBDA_STATUS_CHECK_ROLE_ARN": "<STATUS_CHECK_ROLE_ARN>",
    "LAMBDA_STATUS_CHECK_ARN": "<STATUS_CHECK_LAMBDA_ARN>",
}


@patch.dict(os.environ, mock_arns)
@patch("boto3.client")
@patch.object(Scheduler, "now", return_value=datetime.datetime(2025, 3, 18, 12, 35, 22))
class TestScheduler:
    def test_schedule_batch_processor_retry(self, mock_now, mock_boto3_scheduler):
        subject = Scheduler("123")
        subject.schedule_batch_processor_retry(5)

        mock_boto3_scheduler.return_value.create_schedule.assert_called_once_with(
            Name="lambda_batch_processor_retry",
            ScheduleExpression="at(2025-03-18T12:40:22)",
            Target={
                "RoleArn": "<BATCH_PROCESSOR_ROLE_ARN>",
                "Arn": "<BATCH_PROCESSOR_LAMBDA_ARN>",
                "Input": '{"batch_id": "123", "retries": 1}'
            },
            FlexibleTimeWindow={"Mode": "OFF"}
        )

    def test_schedule_status_check(self, mock_now, mock_boto3_scheduler):
        subject = Scheduler("123")
        subject.schedule_status_check(5)

        mock_boto3_scheduler.return_value.create_schedule.assert_called_once_with(
            Name="lambda_status_check",
            ScheduleExpression="at(2025-03-18T12:40:22)",
            Target={
                "RoleArn": "<STATUS_CHECK_ROLE_ARN>",
                "Arn": "<STATUS_CHECK_LAMBDA_ARN>",
                "Input": '{"batch_id": "123", "retries": 1}'
            },
            FlexibleTimeWindow={"Mode": "OFF"}
        )

    def test_create_schedule(self, mock_now, mock_boto3_scheduler):
        subject = Scheduler("123")
        subject.create_schedule(
            "name",
            10,
            {"RoleArn": "role", "Arn": "arn", "Input": "input"},
        )

        mock_boto3_scheduler.return_value.create_schedule.assert_called_once_with(
            Name="name",
            ScheduleExpression="at(2025-03-18T12:45:22)",
            Target={"RoleArn": "role", "Arn": "arn", "Input": "input"},
            FlexibleTimeWindow={"Mode": "OFF"}
        )

    def test_create_schedule_with_too_many_retries(self, mock_now, mock_boto3_scheduler):
        subject = Scheduler("123", 5)
        subject.create_schedule(
            "name",
            10,
            {"RoleArn": "role", "Arn": "arn", "Input": "input"},
        )

        mock_boto3_scheduler.return_value.create_schedule.assert_not_called()

    def test_create_schedule_with_retries(self, mock_now, mock_boto3_scheduler):
        subject = Scheduler("123", 2)
        subject.create_schedule(
            "name",
            10,
            {"RoleArn": "role", "Arn": "arn", "Input": "input"},
        )

        mock_boto3_scheduler.return_value.create_schedule.assert_called_once_with(
            Name="name",
            ScheduleExpression="at(2025-03-18T12:45:22)",
            Target={"RoleArn": "role", "Arn": "arn", "Input": "input"},
            FlexibleTimeWindow={"Mode": "OFF"}
        )
