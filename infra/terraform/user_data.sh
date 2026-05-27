#!/bin/bash
set -euxo pipefail

# Update system packages
dnf update -y

# Install Docker and buildx
dnf install -y docker
systemctl enable docker
systemctl start docker
usermod -aG docker ec2-user

# Install docker-compose plugin
mkdir -p /usr/local/lib/docker/cli-plugins

COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep '"tag_name"' | cut -d'"' -f4)
curl -SL "https://github.com/docker/compose/releases/download/$${COMPOSE_VERSION}/docker-compose-linux-x86_64" \
  -o /usr/local/lib/docker/cli-plugins/docker-compose
chmod +x /usr/local/lib/docker/cli-plugins/docker-compose

# Install docker-buildx plugin
BUILDX_VERSION=$(curl -s https://api.github.com/repos/docker/buildx/releases/latest | grep '"tag_name"' | cut -d'"' -f4)
curl -SL "https://github.com/docker/buildx/releases/download/$${BUILDX_VERSION}/buildx-$${BUILDX_VERSION}.linux-amd64" \
  -o /usr/local/lib/docker/cli-plugins/docker-buildx
chmod +x /usr/local/lib/docker/cli-plugins/docker-buildx

# Install git
dnf install -y git

# Clone the repository
cd /home/ec2-user
git clone ${github_repo_url} app
cd app

# Fetch the DB password from SSM Parameter Store
DB_PASSWORD=$(aws ssm get-parameter \
  --name "${ssm_param_name}" \
  --with-decryption \
  --query "Parameter.Value" \
  --output text \
  --region "${aws_region}")

# Write environment file for docker-compose
cat > /home/ec2-user/app/.env <<ENVEOF
DATABASE_URL=postgresql://${db_user}:$${DB_PASSWORD}@${db_endpoint}/${db_name}
RUN_SEED=true
LOG_LEVEL=INFO
S3_BUCKET=${s3_bucket}
AWS_REGION=${aws_region}
ENVEOF

chown -R ec2-user:ec2-user /home/ec2-user/app

# Build and start the containers
docker compose -f local/docker-compose.cloud.yml --env-file .env up -d --build
