#!/bin/bash
set -e

# Script to deploy Discord Bot to Lightsail instance
# Usage: ./scripts/deploy.sh <public_ip> <instance_name>

PUBLIC_IP=$1
INSTANCE_NAME=$2

if [ -z "$PUBLIC_IP" ] || [ -z "$INSTANCE_NAME" ]; then
  echo "Usage: $0 <public_ip> <instance_name>"
  exit 1
fi

echo "Deploying to Lightsail instance: $INSTANCE_NAME ($PUBLIC_IP)"

# SSH connection details
SSH_USER="ubuntu"
SSH_HOST="$PUBLIC_IP"
APP_DIR="/opt/discalendar-bot"
# Expand ~ and $HOME to home directory if SSH_KEY_PATH contains them
if [ -n "$SSH_KEY_PATH" ]; then
  # Replace ~ with $HOME, then replace literal $HOME with actual home directory
  SSH_KEY="${SSH_KEY_PATH/#\~/$HOME}"
  SSH_KEY="${SSH_KEY//\$HOME/$HOME}"
else
  SSH_KEY="$HOME/.ssh/lightsail_key"
fi

# Get repository URL from environment or use default
if [ -z "$GITHUB_REPOSITORY" ]; then
  echo "Warning: GITHUB_REPOSITORY not set, using default"
  REPO_URL="https://github.com/owner/repo.git"
else
  REPO_URL="https://github.com/${GITHUB_REPOSITORY}.git"
fi

# Deploy via SSH
ssh -i "${SSH_KEY}" -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
  "${SSH_USER}@${SSH_HOST}" <<EOF
set -e

echo "Updating system packages..."
sudo apt-get update -qq

echo "Cloning/updating repository..."
if [ -d "$APP_DIR/.git" ]; then
  cd $APP_DIR
  git fetch origin
  git reset --hard origin/main
  git clean -fd
else
  sudo rm -rf $APP_DIR
  sudo mkdir -p $APP_DIR
  sudo chown ubuntu:ubuntu $APP_DIR
  git clone $REPO_URL $APP_DIR
  cd $APP_DIR
fi

echo "Configuring AWS credentials for CloudWatch Logs..."
mkdir -p ~/.aws
cat > ~/.aws/credentials <<AWSEOF
[default]
aws_access_key_id = ${AWS_ACCESS_KEY_ID}
aws_secret_access_key = ${AWS_SECRET_ACCESS_KEY}
AWSEOF

cat > ~/.aws/config <<AWSCONFIGEOF
[default]
region = ${AWS_REGION:-ap-northeast-1}
AWSCONFIGEOF

chmod 600 ~/.aws/credentials
chmod 644 ~/.aws/config

echo "Creating .env file..."
cat > .env <<ENVEOF
BOT_TOKEN=${BOT_TOKEN}
APPLICATION_ID=${APPLICATION_ID}
INVITATION_URL=${INVITATION_URL}
SUPABASE_URL=${SUPABASE_URL}
SUPABASE_SERVICE_KEY=${SUPABASE_SERVICE_KEY}
LOG_LEVEL=${LOG_LEVEL:-INFO}
SENTRY_DSN=${SENTRY_DSN:-}
AWS_REGION=${AWS_REGION:-ap-northeast-1}
AWS_CLOUDWATCH_LOG_GROUP=${AWS_CLOUDWATCH_LOG_GROUP}
ENVEOF

echo "Building and starting Docker containers..."
docker compose down || true
docker compose build --no-cache
docker compose up -d

echo "Waiting for container to be healthy..."
sleep 5

echo "Checking container status..."
docker compose ps

echo "Viewing recent logs..."
docker compose logs --tail=50

echo "Deployment completed successfully!"
EOF

echo "Deployment to $INSTANCE_NAME completed!"
