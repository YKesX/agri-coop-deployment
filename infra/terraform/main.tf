provider "aws" {
  region = "eu-central-1"

  default_tags {
    tags = local.common_tags
  }
}

locals {
  project_name = "agri-coop"

  common_tags = {
    Project     = "agri-coop"
    Environment = "demo"
    ManagedBy   = "terraform"
  }
}

data "aws_caller_identity" "current" {}

data "aws_ami" "amazon_linux_2023" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }

  filter {
    name   = "state"
    values = ["available"]
  }
}
