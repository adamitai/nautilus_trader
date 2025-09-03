# Nautilus Trader Arbitrage Tools - Terraform Variables

# General Configuration
variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "nautilus-arbitrage"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be one of: dev, staging, prod."
  }
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-west-2"
}

variable "owner" {
  description = "Owner of the resources"
  type        = string
  default     = "nautilus-team"
}

# Networking Configuration
variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "enable_nat_gateway" {
  description = "Enable NAT Gateway for private subnets"
  type        = bool
  default     = true
}

variable "enable_vpn_gateway" {
  description = "Enable VPN Gateway"
  type        = bool
  default     = false
}

# Compute Configuration
variable "container_image" {
  description = "Docker image for the application"
  type        = string
  default     = "nautilus-arbitrage:latest"
}

variable "container_port" {
  description = "Port the container listens on"
  type        = number
  default     = 8000
}

variable "container_cpu" {
  description = "CPU units for the container (1024 = 1 vCPU)"
  type        = number
  default     = 1024
}

variable "container_memory" {
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

variable "enable_load_balancer" {
  description = "Enable Application Load Balancer"
  type        = bool
  default     = true
}

# Database Configuration
variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.micro"
}

variable "db_allocated_storage" {
  description = "RDS allocated storage in GB"
  type        = number
  default     = 20
}

variable "db_engine_version" {
  description = "PostgreSQL engine version"
  type        = string
  default     = "15.4"
}

# Cache Configuration
variable "cache_node_type" {
  description = "ElastiCache node type"
  type        = string
  default     = "cache.t3.micro"
}

# API Keys (sensitive)
variable "binance_api_key" {
  description = "Binance API key"
  type        = string
  sensitive   = true
  default     = ""
}

variable "binance_api_secret" {
  description = "Binance API secret"
  type        = string
  sensitive   = true
  default     = ""
}

variable "bybit_api_key" {
  description = "Bybit API key"
  type        = string
  sensitive   = true
  default     = ""
}

variable "bybit_api_secret" {
  description = "Bybit API secret"
  type        = string
  sensitive   = true
  default     = ""
}

variable "okx_api_key" {
  description = "OKX API key"
  type        = string
  sensitive   = true
  default     = ""
}

variable "okx_api_secret" {
  description = "OKX API secret"
  type        = string
  sensitive   = true
  default     = ""
}

variable "okx_passphrase" {
  description = "OKX passphrase"
  type        = string
  sensitive   = true
  default     = ""
}

# Environment-specific overrides
variable "environment_config" {
  description = "Environment-specific configuration"
  type = object({
    instance_type     = optional(string, "t3.medium")
    min_capacity      = optional(number, 1)
    max_capacity      = optional(number, 5)
    db_instance_class = optional(string, "db.t3.micro")
    enable_monitoring = optional(bool, true)
  })
  default = {}
}
