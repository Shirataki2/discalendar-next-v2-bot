# Backend configuration
# Note: This file is commented out initially because the S3 bucket
# needs to be created first. Uncomment after initial setup.

terraform {
  backend "s3" {
    bucket         = "discalendar-bot-tfstate"
    key            = "discalendar-bot/terraform.tfstate"
    region         = "ap-northeast-1"
    dynamodb_table = "terraform-state-lock"
    encrypt        = true
  }
}
