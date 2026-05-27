resource "random_password" "db" {
  length  = 24
  special = false
}

locals {
  db_password = coalesce(var.db_password_override, random_password.db.result)
}

resource "aws_ssm_parameter" "db_password" {
  name  = "/${local.project_name}/db-password"
  type  = "SecureString"
  value = local.db_password

  tags = { Name = "${local.project_name}-db-password" }
}

resource "aws_db_subnet_group" "main" {
  name = "${local.project_name}-db-subnets"
  subnet_ids = [
    aws_subnet.private_a.id,
    aws_subnet.private_b.id,
  ]

  tags = { Name = "${local.project_name}-db-subnet-group" }
}

resource "aws_db_instance" "main" {
  identifier     = "${local.project_name}-db"
  engine         = "postgres"
  engine_version = "16"
  instance_class = var.db_instance_class

  allocated_storage = 20
  storage_type      = "gp2"

  db_name  = "agricoop"
  username = "agricoop"
  password = local.db_password

  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.db.id]

  multi_az            = false
  publicly_accessible = false

  skip_final_snapshot  = true
  deletion_protection  = false
  apply_immediately    = true

  tags = { Name = "${local.project_name}-db" }
}
