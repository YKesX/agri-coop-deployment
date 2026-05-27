resource "aws_instance" "app" {
  ami                    = data.aws_ami.amazon_linux_2023.id
  instance_type          = var.app_instance_type
  subnet_id              = aws_subnet.public.id
  vpc_security_group_ids = [aws_security_group.app.id]
  iam_instance_profile   = aws_iam_instance_profile.ec2_app.name
  key_name               = var.key_name != "" ? var.key_name : null

  user_data = templatefile("${path.module}/user_data.sh", {
    github_repo_url = var.github_repo_url
    aws_region      = "eu-central-1"
    db_endpoint     = aws_db_instance.main.endpoint
    db_name         = "agricoop"
    db_user         = "agricoop"
    ssm_param_name  = aws_ssm_parameter.db_password.name
    s3_bucket       = aws_s3_bucket.data.id
  })

  root_block_device {
    volume_size = 20
    volume_type = "gp3"
  }

  tags = { Name = "${local.project_name}-app" }
}

resource "aws_eip" "app" {
  domain = "vpc"
  tags   = { Name = "${local.project_name}-app-eip" }
}

resource "aws_eip_association" "app" {
  instance_id   = aws_instance.app.id
  allocation_id = aws_eip.app.id
}
