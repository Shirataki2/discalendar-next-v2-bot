# Get current AWS account ID
data "aws_caller_identity" "current" {}

# OIDC Provider for GitHub Actions
# Use data source if OIDC provider ARN is not provided, otherwise use variable
data "aws_iam_openid_connect_provider" "github" {
  count = var.oidc_provider_arn == "" ? 1 : 0
  url   = "https://token.actions.githubusercontent.com"
}

locals {
  oidc_provider_arn = var.oidc_provider_arn != "" ? var.oidc_provider_arn : data.aws_iam_openid_connect_provider.github[0].arn
  account_id        = data.aws_caller_identity.current.account_id
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
          Federated = local.oidc_provider_arn
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
          "lightsail:CreateInstanceSnapshot",
          "lightsail:CreateInstances",
          "lightsail:DeleteInstance",
          "lightsail:AllocateStaticIp",
          "lightsail:ReleaseStaticIp",
          "lightsail:AttachStaticIp",
          "lightsail:DetachStaticIp"
        ]
        Resource = [
          aws_lightsail_instance.bot.arn,
          aws_lightsail_static_ip.bot.arn,
          "arn:aws:lightsail:${var.aws_region}:${local.account_id}:instance/*",
          "arn:aws:lightsail:${var.aws_region}:${local.account_id}:static-ip/*"
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
          "s3:GetBucketLocation",
          "s3:GetBucketVersioning",
          "s3:GetBucketPolicy",
          "s3:GetBucketCORS",
          "s3:GetBucketWebsite",
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:GetBucketAcl",
          "s3:PutBucketAcl",
          "s3:PutBucketVersioning",
          "s3:PutBucketPublicAccessBlock",
          "s3:GetBucketPublicAccessBlock",
          "s3:PutEncryptionConfiguration",
          "s3:GetEncryptionConfiguration"
        ]
        Resource = [
          aws_s3_bucket.terraform_state.arn,
          "${aws_s3_bucket.terraform_state.arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "dynamodb:DescribeTable",
          "dynamodb:DescribeContinuousBackups",
          "dynamodb:DescribeTimeToLive",
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:DeleteItem",
          "dynamodb:CreateTable",
          "dynamodb:UpdateTable"
        ]
        Resource = aws_dynamodb_table.terraform_lock.arn
      }
    ]
  })
}

# IAM policy for reading IAM resources (needed for Terraform data source and state refresh)
resource "aws_iam_role_policy" "github_actions_iam_read" {
  name = "${var.instance_name}-github-actions-iam-read-policy"
  role = aws_iam_role.github_actions.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "iam:ListOpenIDConnectProviders",
          "iam:GetOpenIDConnectProvider",
          "iam:GetRole",
          "iam:ListRolePolicies",
          "iam:GetRolePolicy",
          "iam:ListAttachedRolePolicies"
        ]
        Resource = [
          "arn:aws:iam::${local.account_id}:role/${var.instance_name}-github-actions-role",
          "arn:aws:iam::${local.account_id}:role/${var.instance_name}-github-actions-role/*",
          "arn:aws:iam::*:oidc-provider/token.actions.githubusercontent.com"
        ]
      }
    ]
  })
}
