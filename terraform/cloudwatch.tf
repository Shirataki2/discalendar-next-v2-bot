# CloudWatch Logs for Discord Bot
resource "aws_cloudwatch_log_group" "bot" {
  name              = "/aws/lightsail/${var.instance_name}"
  retention_in_days = 7 # 7日間保持（必要に応じて変更可能）

  tags = merge(
    var.tags,
    {
      Name = "${var.instance_name}-logs"
    }
  )
}

# IAM user for CloudWatch Logs access from Lightsail instance
resource "aws_iam_user" "bot_cloudwatch" {
  name = "${var.instance_name}-cloudwatch-user"

  tags = merge(
    var.tags,
    {
      Name = "CloudWatch Logs User for ${var.instance_name}"
    }
  )
}

# IAM policy for CloudWatch Logs write access
resource "aws_iam_user_policy" "bot_cloudwatch_logs" {
  name = "${var.instance_name}-cloudwatch-logs-policy"
  user = aws_iam_user.bot_cloudwatch.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:DescribeLogStreams"
        ]
        Resource = [
          "${aws_cloudwatch_log_group.bot.arn}:*"
        ]
      }
    ]
  })
}

# Access key for IAM user (to be used in Lightsail instance)
resource "aws_iam_access_key" "bot_cloudwatch" {
  user = aws_iam_user.bot_cloudwatch.name
}
