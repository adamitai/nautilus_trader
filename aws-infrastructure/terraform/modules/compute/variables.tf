# Compute Module Variables

variable "name_prefix" {
  description = "Name prefix for resources"
  type        = string
}

variable "cluster_name" {
  description = "Name of the ECS cluster"
  type        = string
}

variable "service_name" {
  description = "Name of the ECS service"
  type        = string
}

variable "container_image" {
  description = "Docker image for the backend application"
  type        = string
}

variable "frontend_image" {
  description = "Docker image for the frontend application"
  type        = string
  default     = "nautilus-arbitrage-frontend:latest"
}

variable "container_port" {
  description = "Port the container listens on"
  type        = number
  default     = 8000
}

variable "cpu" {
  description = "CPU units for the container (1024 = 1 vCPU)"
  type        = number
  default     = 1024
}

variable "memory" {
  description = "Memory for the container in MB"
  type        = number
  default     = 2048
}

variable "min_capacity" {
  description = "Minimum number of tasks"
  type        = number
  default     = 1
}

variable "max_capacity" {
  description = "Maximum number of tasks"
  type        = number
  default     = 10
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}

variable "vpc_id" {
  description = "ID of the VPC"
  type        = string
}

variable "private_subnet_ids" {
  description = "IDs of the private subnets"
  type        = list(string)
}

variable "public_subnet_ids" {
  description = "IDs of the public subnets"
  type        = list(string)
}

variable "security_group_ids" {
  description = "IDs of the security groups"
  type        = list(string)
}

variable "task_execution_role_arn" {
  description = "ARN of the ECS task execution role"
  type        = string
}

variable "task_role_arn" {
  description = "ARN of the ECS task role"
  type        = string
}

variable "secrets_manager_arn" {
  description = "ARN of the secrets manager secret"
  type        = string
}

variable "kms_key_id" {
  description = "KMS key ID for encryption"
  type        = string
}

variable "enable_load_balancer" {
  description = "Enable Application Load Balancer"
  type        = bool
  default     = true
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}
