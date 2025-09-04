# Nautilus Trader Arbitrage Tools - Main Terraform Configuration
# This file orchestrates the deployment of the complete AWS infrastructure

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.1"
    }
  }
  
  # Configure remote state storage
  # Backend configuration is handled by backend.tf file
}

# Configure the AWS Provider
provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Project     = "nautilus-arbitrage"
      Environment = var.environment
      ManagedBy   = "terraform"
      Owner       = var.owner
    }
  }
}

# Data sources
data "aws_availability_zones" "available" {
  state = "available"
}

data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

# Local values
locals {
  name_prefix = "${var.project_name}-${var.environment}"
  
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    Owner       = var.owner
    ManagedBy   = "terraform"
  }
  
  # VPC Configuration
  vpc_cidr = var.vpc_cidr
  azs      = slice(data.aws_availability_zones.available.names, 0, 3)
  
  # Subnet CIDRs
  public_subnets  = [for k, v in local.azs : cidrsubnet(local.vpc_cidr, 8, k)]
  private_subnets = [for k, v in local.azs : cidrsubnet(local.vpc_cidr, 8, k + 10)]
  database_subnets = [for k, v in local.azs : cidrsubnet(local.vpc_cidr, 8, k + 20)]
}

# Random password for RDS
resource "random_password" "db_password" {
  length  = 16
  special = true
}

# KMS Key for encryption
resource "aws_kms_key" "main" {
  description             = "KMS key for ${local.name_prefix}"
  deletion_window_in_days = 7
  
  tags = local.common_tags
}

resource "aws_kms_alias" "main" {
  name          = "alias/${local.name_prefix}"
  target_key_id = aws_kms_key.main.key_id
}

# KMS Key Policy for CloudWatch Logs
resource "aws_kms_key_policy" "main" {
  key_id = aws_kms_key.main.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "Enable IAM User Permissions"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
        }
        Action   = "kms:*"
        Resource = "*"
      },
      {
        Sid    = "Allow CloudWatch Logs"
        Effect = "Allow"
        Principal = {
          Service = "logs.${data.aws_region.current.name}.amazonaws.com"
        }
        Action = [
          "kms:Encrypt",
          "kms:Decrypt",
          "kms:ReEncrypt*",
          "kms:GenerateDataKey*",
          "kms:DescribeKey"
        ]
        Resource = "*"
        Condition = {
          ArnEquals = {
            "kms:EncryptionContext:aws:logs:arn" = "arn:aws:logs:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:log-group:/ecs/${local.name_prefix}*"
          }
        }
      }
    ]
  })
}

# Networking Module
module "networking" {
  source = "./modules/networking"
  
  name_prefix = local.name_prefix
  vpc_cidr    = local.vpc_cidr
  azs         = local.azs
  
  public_subnets   = local.public_subnets
  private_subnets  = local.private_subnets
  database_subnets = local.database_subnets
  
  enable_nat_gateway = var.enable_nat_gateway
  enable_vpn_gateway = var.enable_vpn_gateway
  
  tags = local.common_tags
}

# Security Module
module "security" {
  source = "./modules/security"
  
  name_prefix = local.name_prefix
  vpc_id      = module.networking.vpc_id
  
  # API Keys for exchanges
  binance_api_key    = var.binance_api_key
  binance_api_secret = var.binance_api_secret
  bybit_api_key      = var.bybit_api_key
  bybit_api_secret   = var.bybit_api_secret
  okx_api_key        = var.okx_api_key
  okx_api_secret     = var.okx_api_secret
  okx_passphrase     = var.okx_passphrase
  
  kms_key_id = aws_kms_key.main.key_id
  
  tags = local.common_tags
}

# Storage Module
module "storage" {
  source = "./modules/storage"
  
  name_prefix = local.name_prefix
  
  # S3 Configuration
  s3_bucket_name = "${local.name_prefix}-data"
  
  # RDS Configuration
  db_instance_class    = var.db_instance_class
  db_allocated_storage = var.db_allocated_storage
  db_engine_version    = var.db_engine_version
  
  # ElastiCache Configuration
  cache_node_type = var.cache_node_type
  
  # Networking
  vpc_id             = module.networking.vpc_id
  private_subnet_ids = module.networking.private_subnet_ids
  database_subnet_ids = module.networking.database_subnet_ids
  
  # Security
  db_password = random_password.db_password.result
  kms_key_id  = aws_kms_key.main.arn
  rds_security_group_id = module.security.rds_security_group_id
  elasticache_security_group_id = module.security.elasticache_security_group_id
  
  tags = local.common_tags
}

# Compute Module
module "compute" {
  source = "./modules/compute"
  
  name_prefix = local.name_prefix
  
  # ECS Configuration
  cluster_name = "${local.name_prefix}-cluster"
  service_name = "${local.name_prefix}-service"
  
  # Container Configuration
  container_image = var.container_image
  container_port  = var.container_port
  cpu             = var.container_cpu
  memory          = var.container_memory
  
  # Auto Scaling
  min_capacity = var.min_capacity
  max_capacity = var.max_capacity
  
  # Networking
  vpc_id             = module.networking.vpc_id
  private_subnet_ids = module.networking.private_subnet_ids
  public_subnet_ids  = module.networking.public_subnet_ids
  
  # Security
  task_execution_role_arn = module.security.ecs_task_execution_role_arn
  task_role_arn          = module.security.ecs_task_role_arn
  security_group_ids     = [module.security.ecs_security_group_id]
  secrets_manager_arn    = module.security.secrets_manager_arn
  kms_key_id            = aws_kms_key.main.arn
  
  # Load Balancer
  enable_load_balancer = var.enable_load_balancer
  
  tags = local.common_tags
}

# Monitoring Module
module "monitoring" {
  source = "./modules/monitoring"
  
  name_prefix = local.name_prefix
  
  # ECS Cluster
  ecs_cluster_name = module.compute.ecs_cluster_name
  ecs_service_name = module.compute.ecs_service_name
  
  # S3 Bucket for logs
  s3_bucket_name = module.storage.s3_bucket_name
  
  # SNS Topic for alerts
  sns_topic_arn = module.security.sns_topic_arn
  
  # Log group name
  log_group_name = module.compute.cloudwatch_log_group_name
  
  # ALB ARN suffix
  alb_arn_suffix = module.compute.load_balancer_arn != null ? split("/", module.compute.load_balancer_arn)[1] : ""
  
  # RDS identifier
  rds_identifier = module.storage.rds_identifier
  
  # ElastiCache cluster ID
  elasticache_cluster_id = module.storage.elasticache_endpoint != null ? split(".", module.storage.elasticache_endpoint)[0] : ""
  
  tags = local.common_tags
}

# Outputs
output "vpc_id" {
  description = "ID of the VPC"
  value       = module.networking.vpc_id
}

output "ecs_cluster_name" {
  description = "Name of the ECS cluster"
  value       = module.compute.ecs_cluster_name
}

output "ecs_service_name" {
  description = "Name of the ECS service"
  value       = module.compute.ecs_service_name
}

output "load_balancer_dns" {
  description = "DNS name of the load balancer"
  value       = module.compute.load_balancer_dns
}

output "s3_bucket_name" {
  description = "Name of the S3 bucket"
  value       = module.storage.s3_bucket_name
}

output "rds_endpoint" {
  description = "RDS instance endpoint"
  value       = module.storage.rds_endpoint
  sensitive   = true
}

output "secrets_manager_arn" {
  description = "ARN of the secrets manager secret"
  value       = module.security.secrets_manager_arn
}
