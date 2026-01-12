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

# Attach AdministratorAccess policy to GitHub Actions role
# Note: This grants full AWS access. For production, consider using more restrictive policies.
resource "aws_iam_role_policy_attachment" "github_actions_administrator" {
  role       = aws_iam_role.github_actions.name
  policy_arn = "arn:aws:iam::aws:policy/AdministratorAccess"
}
