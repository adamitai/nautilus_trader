# Monitoring Module Variables

variable "name_prefix" {
  description = "Name prefix for resources"
  type        = string
}

variable "ecs_cluster_name" {
  description = "Name of the ECS cluster"
  type        = string
}

variable "ecs_service_name" {
  description = "Name of the ECS service"
  type        = string
}

variable "log_group_name" {
  description = "Name of the CloudWatch log group"
  type        = string
}

variable "s3_bucket_name" {
  description = "Name of the S3 bucket"
  type        = string
}

variable "sns_topic_arn" {
  description = "ARN of the SNS topic for alerts"
  type        = string
}

variable "alb_arn_suffix" {
  description = "ARN suffix of the Application Load Balancer"
  type        = string
  default     = ""
}

variable "rds_identifier" {
  description = "RDS instance identifier"
  type        = string
  default     = ""
}

variable "elasticache_cluster_id" {
  description = "ElastiCache cluster ID"
  type        = string
  default     = ""
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}
