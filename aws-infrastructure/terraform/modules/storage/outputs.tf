# Storage Module Outputs

output "s3_bucket_name" {
  description = "Name of the S3 bucket"
  value       = aws_s3_bucket.main.bucket
}

output "s3_bucket_arn" {
  description = "ARN of the S3 bucket"
  value       = aws_s3_bucket.main.arn
}

output "s3_bucket_domain_name" {
  description = "Domain name of the S3 bucket"
  value       = aws_s3_bucket.main.bucket_domain_name
}

output "rds_endpoint" {
  description = "RDS instance endpoint"
  value       = aws_db_instance.main.endpoint
}

output "rds_port" {
  description = "RDS instance port"
  value       = aws_db_instance.main.port
}

output "rds_identifier" {
  description = "RDS instance identifier"
  value       = aws_db_instance.main.identifier
}

output "rds_arn" {
  description = "RDS instance ARN"
  value       = aws_db_instance.main.arn
}

output "elasticache_endpoint" {
  description = "ElastiCache primary endpoint"
  value       = aws_elasticache_replication_group.main.primary_endpoint_address
}

output "elasticache_port" {
  description = "ElastiCache port"
  value       = aws_elasticache_replication_group.main.port
}

output "elasticache_reader_endpoint" {
  description = "ElastiCache reader endpoint"
  value       = aws_elasticache_replication_group.main.reader_endpoint_address
}

output "elasticache_arn" {
  description = "ElastiCache replication group ARN"
  value       = aws_elasticache_replication_group.main.arn
}
