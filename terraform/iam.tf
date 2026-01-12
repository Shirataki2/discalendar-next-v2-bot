# OIDC Provider for GitHub Actions
data "aws_iam_openid_connect_provider" "github" {
  url = "https://token.actions.githubusercontent.com"
}

# IAM role for GitHub Actions
resource "aws_iam_role" "github_actions" {
  name = "${var.instance_name}-github-actions-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Federated = data.aws_iam_openid_connect_provider.github.arn
        }
        Action = "sts:AssumeRoleWithWebIdentity"
        Condition = {
          StringEquals = {
            "token.actions.githubusercontent.com:aud" = "sts.amazonaws.com"
          }
          StringLike = {
            "token.actions.githubusercontent.com:sub" = "repo:${var.github_repository}:*"
          }
        }
      }
    ]
  })

  tags = merge(
    var.tags,
    {
      Name = "GitHub Actions Role for ${var.instance_name}"
    }
  )
}

# IAM policy for Lightsail operations
resource "aws_iam_role_policy" "github_actions_lightsail" {
  name = "${var.instance_name}-github-actions-lightsail-policy"
  role = aws_iam_role.github_actions.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "lightsail:GetInstance",
          "lightsail:GetInstances",
          "lightsail:GetInstanceAccessDetails",
          "lightsail:GetStaticIp",
          "lightsail:GetStaticIps",
          "lightsail:UpdateInstanceMetadataOptions",
          "lightsail:StartInstance",
          "lightsail:StopInstance",
          "lightsail:RebootInstance",
          "lightsail:GetInstanceSnapshot",
          "lightsail:CreateInstanceSnapshot"
        ]
        Resource = [
          aws_lightsail_instance.bot.arn,
          aws_lightsail_static_ip.bot.arn
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "lightsail:DownloadDefaultKeyPair"
        ]
        Resource = "*"
      }
    ]
  })
}

# IAM policy for S3 and DynamoDB (for Terraform state)
resource "aws_iam_role_policy" "github_actions_terraform" {
  name = "${var.instance_name}-github-actions-terraform-policy"
  role = aws_iam_role.github_actions.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:ListBucket",
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject"
        ]
        Resource = [
          aws_s3_bucket.terraform_state.arn,
          "${aws_s3_bucket.terraform_state.arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:DeleteItem"
        ]
        Resource = aws_dynamodb_table.terraform_lock.arn
      }
    ]
  })
}
