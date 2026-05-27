variable "alert_email" {
  description = "Email address for CloudWatch alarm notifications"
  type        = string
}

variable "db_password_override" {
  description = "Optional manual DB password. If null, a random password is generated."
  type        = string
  default     = null
  sensitive   = true
}

variable "github_repo_url" {
  description = "HTTPS URL of the GitHub repo to clone on the EC2 instance"
  type        = string
  default     = "https://github.com/YKesX/agri-coop-deployment.git"
}

variable "app_instance_type" {
  description = "EC2 instance type for the application server"
  type        = string
  default     = "t2.micro"
}

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.micro"
}
