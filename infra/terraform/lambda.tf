data "archive_file" "lambda" {
  type        = "zip"
  source_dir  = "${path.module}/../../apps/lambda-sensor-processor"
  output_path = "${path.module}/lambda-sensor-processor.zip"
}

resource "aws_lambda_function" "sensor_aggregator" {
  function_name    = "${local.project_name}-sensor-aggregator"
  filename         = data.archive_file.lambda.output_path
  source_code_hash = data.archive_file.lambda.output_base64sha256
  handler          = "handler.handler"
  runtime          = "python3.12"
  timeout          = 60
  memory_size      = 128
  role             = aws_iam_role.lambda.arn

  vpc_config {
    subnet_ids         = [aws_subnet.private_a.id, aws_subnet.private_b.id]
    security_group_ids = [aws_security_group.lambda.id]
  }

  environment {
    variables = {
      DB_HOST            = aws_db_instance.main.address
      DB_PORT            = "5432"
      DB_NAME            = "agricoop"
      DB_USER            = "agricoop"
      DB_PASSWORD        = local.db_password
      SNS_TOPIC_ARN      = aws_sns_topic.alerts.arn
      MOISTURE_THRESHOLD = "35"
    }
  }

  tags = { Name = "${local.project_name}-sensor-aggregator" }
}

resource "aws_cloudwatch_log_group" "lambda" {
  name              = "/aws/lambda/${aws_lambda_function.sensor_aggregator.function_name}"
  retention_in_days = 7

  tags = { Name = "${local.project_name}-lambda-logs" }
}

resource "aws_cloudwatch_event_rule" "lambda_schedule" {
  name                = "${local.project_name}-sensor-schedule"
  description         = "Trigger sensor aggregator Lambda every hour"
  schedule_expression = "rate(1 hour)"

  tags = { Name = "${local.project_name}-sensor-schedule" }
}

resource "aws_cloudwatch_event_target" "lambda" {
  rule      = aws_cloudwatch_event_rule.lambda_schedule.name
  target_id = "sensor-aggregator"
  arn       = aws_lambda_function.sensor_aggregator.arn
}

resource "aws_lambda_permission" "eventbridge" {
  statement_id  = "AllowEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.sensor_aggregator.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.lambda_schedule.arn
}
