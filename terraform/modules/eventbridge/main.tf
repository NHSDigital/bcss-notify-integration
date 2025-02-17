# Schedule to trigger the Lambda at 8:00 every day
resource "aws_cloudwatch_event_rule" "batch_processor_8am_schedule" {
  name                = "batch-request-8am-schedule-${var.environment}"
  description         = "Schedule for batch request lambda at 8:00 AM"
  schedule_expression = "cron(0 8 * * ? *)" # Runs at 8:00 every day
}

# Schedule to trigger the Lambda at 9:00 every day
resource "aws_cloudwatch_event_rule" "batch_processor_9am_schedule" {
  name                = "batch-request-9am-schedule-${var.environment}"
  description         = "Schedule for batch request lambda at 9:00 AM"
  schedule_expression = "cron(0 9 * * ? *)" # Runs at 9:00 every day
}

resource "aws_cloudwatch_event_target" "batch_processor_8am_event_target" {
  rule      = aws_cloudwatch_event_rule.batch_processor_8am_schedule.name # Point to the first rule
  target_id = "batch_processor_8am_event_target"
  arn       = var.batch_processor_lambda_arn
}

resource "aws_cloudwatch_event_target" "batch_processor_9am_event_target" {
  rule      = aws_cloudwatch_event_rule.batch_processor_9am_schedule.name # Point to the first rule
  target_id = "batch_processor_9am_event_target"
  arn       = var.batch_processor_lambda_arn
}

# Grant CloudWatch Events permission to invoke the Lambda function
resource "aws_lambda_permission" "allow_cloudwatch_8am_to_call_batch_processor" {
  statement_id  = "AllowExecutionFromCloudWatch-8am"
  action        = "lambda:InvokeFunction"
  function_name = var.batch_processor_lambda_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.batch_processor_8am_schedule.arn
}

resource "aws_lambda_permission" "allow_cloudwatch_9am_to_call_batch_processor" {
  statement_id  = "AllowExecutionFromCloudWatch-9am"
  action        = "lambda:InvokeFunction"
  function_name = var.batch_processor_lambda_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.batch_processor_9am_schedule.arn
}