output "lightsail_instance_name" {
  description = "Name of the Lightsail instance"
  value       = aws_lightsail_instance.bot.name
}

output "lightsail_instance_arn" {
  description = "ARN of the Lightsail instance"
  value       = aws_lightsail_instance.bot.arn
}

output "lightsail_instance_public_ip" {
  description = "Public IP address of the Lightsail instance"
  value       = aws_lightsail_instance.bot.public_ip_address
}

output "lightsail_instance_private_ip" {
  description = "Private IP address of the Lightsail instance"
  value       = aws_lightsail_instance.bot.private_ip_address
}

output "iam_role_arn" {
  description = "ARN of the IAM role for GitHub Actions OIDC"
  value       = aws_iam_role.github_actions.arn
}

output "s3_bucket_name" {
  description = "Name of the S3 bucket for Terraform state"
  value       = aws_s3_bucket.terraform_state.id
}

output "dynamodb_table_name" {
  description = "Name of the DynamoDB table for state locking"
  value       = aws_dynamodb_table.terraform_lock.name
}
