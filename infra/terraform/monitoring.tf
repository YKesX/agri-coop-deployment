resource "aws_sns_topic" "alerts" {
  name = "${local.project_name}-alerts"
  tags = { Name = "${local.project_name}-alerts" }
}

resource "aws_sns_topic_subscription" "email" {
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "email"
  endpoint  = var.alert_email
}

## --- CloudWatch Alarms ---

resource "aws_cloudwatch_metric_alarm" "ec2_cpu" {
  alarm_name          = "${local.project_name}-ec2-cpu-high"
  alarm_description   = "EC2 CPU utilization above 80% for 4 minutes"
  namespace           = "AWS/EC2"
  metric_name         = "CPUUtilization"
  statistic           = "Average"
  period              = 120
  evaluation_periods  = 2
  threshold           = 80
  comparison_operator = "GreaterThanThreshold"

  dimensions = {
    InstanceId = aws_instance.app.id
  }

  alarm_actions = [aws_sns_topic.alerts.arn]

  tags = { Name = "${local.project_name}-ec2-cpu-alarm" }
}

resource "aws_cloudwatch_metric_alarm" "rds_storage" {
  alarm_name          = "${local.project_name}-rds-low-storage"
  alarm_description   = "RDS free storage below 2 GB"
  namespace           = "AWS/RDS"
  metric_name         = "FreeStorageSpace"
  statistic           = "Average"
  period              = 300
  evaluation_periods  = 1
  threshold           = 2000000000
  comparison_operator = "LessThanThreshold"

  dimensions = {
    DBInstanceIdentifier = aws_db_instance.main.identifier
  }

  alarm_actions = [aws_sns_topic.alerts.arn]

  tags = { Name = "${local.project_name}-rds-storage-alarm" }
}

resource "aws_cloudwatch_metric_alarm" "lambda_errors" {
  alarm_name          = "${local.project_name}-lambda-errors"
  alarm_description   = "Lambda errors detected in 5-minute window"
  namespace           = "AWS/Lambda"
  metric_name         = "Errors"
  statistic           = "Sum"
  period              = 300
  evaluation_periods  = 1
  threshold           = 0
  comparison_operator = "GreaterThanThreshold"

  dimensions = {
    FunctionName = aws_lambda_function.sensor_aggregator.function_name
  }

  alarm_actions = [aws_sns_topic.alerts.arn]

  tags = { Name = "${local.project_name}-lambda-errors-alarm" }
}

## --- CloudWatch Dashboard ---

resource "aws_cloudwatch_dashboard" "main" {
  dashboard_name = "${local.project_name}-dashboard"

  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "metric"
        x      = 0
        y      = 0
        width  = 12
        height = 6
        properties = {
          title   = "EC2 CPU Utilization"
          metrics = [["AWS/EC2", "CPUUtilization", "InstanceId", aws_instance.app.id]]
          period  = 300
          region  = "eu-central-1"
          stat    = "Average"
        }
      },
      {
        type   = "metric"
        x      = 12
        y      = 0
        width  = 12
        height = 6
        properties = {
          title = "RDS CPU & Storage"
          metrics = [
            ["AWS/RDS", "CPUUtilization", "DBInstanceIdentifier", aws_db_instance.main.identifier],
            ["AWS/RDS", "FreeStorageSpace", "DBInstanceIdentifier", aws_db_instance.main.identifier, { yAxis = "right" }]
          ]
          period = 300
          region = "eu-central-1"
          stat   = "Average"
        }
      },
      {
        type   = "metric"
        x      = 0
        y      = 6
        width  = 12
        height = 6
        properties = {
          title   = "S3 Bucket Size"
          metrics = [["AWS/S3", "BucketSizeBytes", "BucketName", aws_s3_bucket.data.id, "StorageType", "StandardStorage"]]
          period  = 86400
          region  = "eu-central-1"
          stat    = "Average"
        }
      },
      {
        type   = "metric"
        x      = 12
        y      = 6
        width  = 12
        height = 6
        properties = {
          title = "Lambda Invocations & Errors"
          metrics = [
            ["AWS/Lambda", "Invocations", "FunctionName", aws_lambda_function.sensor_aggregator.function_name],
            ["AWS/Lambda", "Errors", "FunctionName", aws_lambda_function.sensor_aggregator.function_name, { color = "#d62728" }]
          ]
          period = 300
          region = "eu-central-1"
          stat   = "Sum"
        }
      }
    ]
  })
}
