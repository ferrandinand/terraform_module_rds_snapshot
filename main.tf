data "aws_region" "current" {
  current = true
}

data "archive_file" "lambda_rds_backup_zip" {
  type = "zip"
  source_dir = "${path.module}/rds_backup/"
  output_path = "${path.module}/files/lambda_rds_backup.zip"
}

resource "aws_lambda_function" "rds_backup" {
  filename = "${path.module}/files/lambda_rds_backup.zip"
  function_name = "rds_backup_lambda"
  role = "${aws_iam_role.lambda_rds_backup.arn}"
  handler = "create_backup.handler"
  source_code_hash = "${base64sha256(file("files/lambda_rds_backup.zip"))}"
  runtime = "python2.7"
  timeout = 300

  lifecycle {
    ignore_changes = ["filename"]
  }
}

## Cloudwatch configuration

resource "aws_cloudwatch_event_rule" "rds_backup_interval" {
  name = "rdsbackup-every-${var.rds_backup_interval}-minutes"
  description = "Fires every ${var.rds_backup_interval} minutes"
  schedule_expression = "rate(${var.rds_backup_interval} minutes)"
}


resource "aws_cloudwatch_event_target" "create_rds_backup" {
  rule = "${aws_cloudwatch_event_rule.rds_backup_interval.name}"
  target_id = "rds_backup"
  arn = "${aws_lambda_function.rds_backup.arn}"
}

resource "aws_lambda_permission" "allow_cloudwatch_to_call_lambda_rds_backup" {
  statement_id = "AllowExecutionFromCloudWatch"
  action = "lambda:InvokeFunction"
  function_name = "${aws_lambda_function.rds_backup.function_name}"
  principal = "events.amazonaws.com"
  source_arn = "${aws_cloudwatch_event_rule.rds_backup_interval.arn}"
}


# Watch and clean
resource "aws_lambda_function" "rds_clean_backup" {
  filename = "${path.module}/files/lambda_dynamo_backup.zip"
  function_name = "rds_backup_clean_and_watch"
  role = "${aws_iam_role.lambda_rds_backup.arn}"
  handler = "clean_and_watch.handler"
  source_code_hash = "${base64sha256(file("files/lambda_rds_backup.zip"))}"
  runtime = "python2.7"
  timeout = 300
  environment {
      variables = {
          BACKUP_RETENTION_DAYS = "${var.backup_retention_days}"
      }
  }

  lifecycle {
    ignore_changes = ["filename"]
  }
}

## Cloudwatch configuration

resource "aws_cloudwatch_event_rule" "rds_backup_interval_cleaner" {
    name = "rdscleanbackup-every-${var.rds_backup_interval}-minutes"
    description = "Fires every ${var.rds_backup_interval} minutes"
    schedule_expression = "rate(${var.rds_backup_interval} minutes)"
}


resource "aws_cloudwatch_event_target" "create_rds_backup_cleaner" {
    rule = "${aws_cloudwatch_event_rule.rds_backup_interval.name}"
    target_id = "rds_backup_cleaner"
    arn = "${aws_lambda_function.rds_clean_backup.arn}"
}

resource "aws_lambda_permission" "allow_cloudwatch_to_call_lambda_rds_backup_cleaner" {
    statement_id = "AllowExecutionFromCloudWatch"
    action = "lambda:InvokeFunction"
    function_name = "${aws_lambda_function.rds_clean_backup.function_name}"
    principal = "events.amazonaws.com"
    source_arn = "${aws_cloudwatch_event_rule.rds_backup_interval_cleaner.arn}"
}

