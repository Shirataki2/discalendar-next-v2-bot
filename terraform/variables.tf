variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "ap-northeast-1"
}

variable "instance_name" {
  description = "Name of the Lightsail instance"
  type        = string
  default     = "discalendar-bot"
}

variable "bundle_id" {
  description = "Lightsail bundle ID (nano_2_0 for smallest plan)"
  type        = string
  default     = "nano_2_0"
}

variable "blueprint_id" {
  description = "Lightsail blueprint ID (Ubuntu 22.04 LTS)"
  type        = string
  default     = "ubuntu_22_04"
}

variable "github_repository" {
  description = "GitHub repository in format 'owner/repo'"
  type        = string
}

variable "s3_bucket_name" {
  description = "S3 bucket name for Terraform state (must be globally unique)"
  type        = string
}

variable "dynamodb_table_name" {
  description = "DynamoDB table name for state locking"
  type        = string
  default     = "terraform-state-lock"
}

variable "tags" {
  description = "Additional tags for resources"
  type        = map(string)
  default     = {}
}

variable "oidc_provider_arn" {
  description = "ARN of the GitHub Actions OIDC provider (optional, will be looked up if not provided)"
  type        = string
  default     = ""
}
