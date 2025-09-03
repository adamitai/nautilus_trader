# Security Guide - Nautilus Trader Arbitrage Tools

This guide outlines the security measures implemented in the AWS infrastructure for the Nautilus Trader arbitrage monitoring system.

## 🔒 Security Architecture

### Defense in Depth

The infrastructure implements multiple layers of security:

1. **Network Security**: VPC isolation, security groups, NACLs
2. **Identity & Access**: IAM roles, policies, MFA
3. **Data Protection**: Encryption at rest and in transit
4. **Secrets Management**: AWS Secrets Manager, KMS
5. **Monitoring**: CloudTrail, CloudWatch, GuardDuty
6. **Compliance**: SOC 2, PCI DSS considerations

## 🌐 Network Security

### VPC Configuration

```hcl
# Isolated VPC with private subnets
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
}
```

**Security Features:**
- **Private Subnets**: Application runs in isolated private subnets
- **Public Subnets**: Only load balancers and NAT gateways
- **Database Subnets**: Dedicated subnets for RDS
- **No Direct Internet Access**: Applications cannot be reached directly

### Security Groups

```hcl
# ECS Tasks Security Group
resource "aws_security_group" "ecs_tasks" {
  ingress {
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]  # Only from within VPC
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]  # Outbound internet access
  }
}
```

**Security Rules:**
- **Ingress**: Only necessary ports from trusted sources
- **Egress**: Controlled outbound access
- **Least Privilege**: Minimal required permissions

### Network ACLs

```hcl
# Additional layer of network security
resource "aws_network_acl" "private" {
  vpc_id = aws_vpc.main.id
  
  # Allow HTTP/HTTPS outbound
  egress {
    protocol   = "tcp"
    rule_no    = 100
    action     = "allow"
    cidr_block = "0.0.0.0/0"
    from_port  = 80
    to_port    = 443
  }
  
  # Deny all other traffic
  egress {
    protocol   = "-1"
    rule_no    = 32767
    action     = "deny"
    cidr_block = "0.0.0.0/0"
    from_port  = 0
    to_port    = 0
  }
}
```

## 🔐 Identity and Access Management

### IAM Roles

```hcl
# ECS Task Execution Role
resource "aws_iam_role" "ecs_task_execution_role" {
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}
```

**Role Principles:**
- **Service-Specific Roles**: Each service has its own role
- **Least Privilege**: Minimal required permissions
- **No Long-Term Credentials**: Use IAM roles, not access keys
- **Regular Rotation**: Automatic credential rotation

### IAM Policies

```hcl
# Granular permissions for ECS tasks
resource "aws_iam_role_policy" "ecs_task_policy" {
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject"
        ]
        Resource = "arn:aws:s3:::nautilus-arbitrage-data/*"
      },
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = aws_secretsmanager_secret.api_keys.arn
      }
    ]
  })
}
```

**Policy Features:**
- **Resource-Specific**: Limit access to specific resources
- **Action-Specific**: Only required actions allowed
- **Condition-Based**: Additional access controls
- **Regular Audits**: Review and update permissions

## 🔑 Secrets Management

### AWS Secrets Manager

```hcl
# Secure storage of API keys
resource "aws_secretsmanager_secret" "api_keys" {
  name                    = "nautilus-arbitrage-api-keys"
  description             = "API keys for cryptocurrency exchanges"
  kms_key_id              = aws_kms_key.main.key_id
  recovery_window_in_days = 7
}
```

**Security Features:**
- **Encryption**: KMS encryption at rest
- **Access Logging**: CloudTrail integration
- **Automatic Rotation**: Regular key rotation
- **Version Control**: Multiple secret versions
- **Access Control**: IAM-based access

### KMS Encryption

```hcl
# Customer-managed encryption key
resource "aws_kms_key" "main" {
  description             = "KMS key for Nautilus Arbitrage"
  deletion_window_in_days = 7
  enable_key_rotation     = true
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
        }
        Action   = "kms:*"
        Resource = "*"
      }
    ]
  })
}
```

**Encryption Features:**
- **Customer-Managed**: Full control over encryption keys
- **Automatic Rotation**: Annual key rotation
- **Audit Trail**: All key usage logged
- **Cross-Service**: Encrypts data across AWS services

## 🛡️ Data Protection

### Encryption at Rest

```hcl
# RDS encryption
resource "aws_db_instance" "main" {
  storage_encrypted = true
  kms_key_id       = aws_kms_key.main.key_id
}

# S3 encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "main" {
  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.main.key_id
      sse_algorithm     = "aws:kms"
    }
  }
}
```

### Encryption in Transit

```hcl
# HTTPS-only load balancer
resource "aws_lb_listener" "main" {
  port     = "443"
  protocol = "HTTPS"
  ssl_policy = "ELBSecurityPolicy-TLS-1-2-2017-01"
  certificate_arn = aws_acm_certificate.main.arn
}
```

**Encryption Standards:**
- **TLS 1.2+**: All communications encrypted
- **Perfect Forward Secrecy**: Unique session keys
- **Certificate Management**: ACM for SSL certificates
- **HSTS**: HTTP Strict Transport Security

## 📊 Monitoring and Logging

### CloudTrail

```hcl
# Comprehensive audit logging
resource "aws_cloudtrail" "main" {
  name                          = "nautilus-arbitrage-trail"
  s3_bucket_name               = aws_s3_bucket.cloudtrail.id
  include_global_service_events = true
  is_multi_region_trail        = true
  enable_logging               = true
}
```

**Audit Features:**
- **API Calls**: All AWS API calls logged
- **Data Events**: S3 and Lambda data events
- **Insight Events**: Unusual API activity
- **Multi-Region**: Global trail coverage

### CloudWatch Logs

```hcl
# Application logging
resource "aws_cloudwatch_log_group" "main" {
  name              = "/ecs/nautilus-arbitrage"
  retention_in_days = 30
  kms_key_id        = aws_kms_key.main.key_id
}
```

**Logging Features:**
- **Structured Logging**: JSON-formatted logs
- **Log Aggregation**: Centralized log collection
- **Retention Policies**: Configurable retention periods
- **Log Analysis**: CloudWatch Insights queries

### GuardDuty

```hcl
# Threat detection
resource "aws_guardduty_detector" "main" {
  enable = true
  
  datasources {
    s3_logs {
      enable = true
    }
    kubernetes {
      audit_logs {
        enable = true
      }
    }
  }
}
```

**Threat Detection:**
- **Malware Detection**: Scan for malicious activity
- **Anomaly Detection**: Unusual behavior patterns
- **Threat Intelligence**: Global threat feeds
- **Automated Response**: Integration with Lambda

## 🔍 Compliance and Governance

### AWS Config

```hcl
# Configuration compliance
resource "aws_config_configuration_recorder" "main" {
  name     = "nautilus-arbitrage-recorder"
  role_arn = aws_iam_role.config.arn
  
  recording_group {
    all_supported                 = true
    include_global_resource_types = true
  }
}
```

**Compliance Features:**
- **Configuration History**: Track resource changes
- **Compliance Rules**: Automated compliance checks
- **Remediation**: Automatic non-compliance fixes
- **Reporting**: Compliance dashboards

### Security Hub

```hcl
# Centralized security findings
resource "aws_securityhub_account" "main" {
  enable_default_standards = true
}
```

**Security Features:**
- **Centralized Findings**: All security findings in one place
- **Standards Compliance**: CIS, PCI DSS, SOC 2
- **Automated Checks**: Continuous compliance monitoring
- **Integration**: Works with other AWS security services

## 🚨 Incident Response

### Automated Response

```hcl
# Lambda function for incident response
resource "aws_lambda_function" "incident_response" {
  filename         = "incident_response.zip"
  function_name    = "nautilus-arbitrage-incident-response"
  role            = aws_iam_role.lambda.arn
  handler         = "index.handler"
  runtime         = "python3.9"
  
  environment {
    variables = {
      SNS_TOPIC_ARN = aws_sns_topic.alerts.arn
    }
  }
}
```

**Response Features:**
- **Automated Alerts**: Immediate notification of security events
- **Isolation**: Automatic resource isolation if needed
- **Forensics**: Log collection and analysis
- **Recovery**: Automated recovery procedures

### Backup and Recovery

```hcl
# Automated backups
resource "aws_backup_vault" "main" {
  name        = "nautilus-arbitrage-backup-vault"
  kms_key_arn = aws_kms_key.main.arn
}

resource "aws_backup_plan" "main" {
  name = "nautilus-arbitrage-backup-plan"
  
  rule {
    rule_name         = "daily_backup"
    target_vault_name = aws_backup_vault.main.name
    schedule          = "cron(0 2 * * ? *)"  # Daily at 2 AM
    
    lifecycle {
      cold_storage_after = 30
      delete_after       = 90
    }
  }
}
```

## 🔧 Security Best Practices

### Application Security

1. **Input Validation**: Validate all user inputs
2. **Output Encoding**: Prevent XSS attacks
3. **Authentication**: Strong authentication mechanisms
4. **Authorization**: Role-based access control
5. **Session Management**: Secure session handling

### Infrastructure Security

1. **Regular Updates**: Keep all components updated
2. **Vulnerability Scanning**: Regular security scans
3. **Penetration Testing**: Periodic security testing
4. **Security Training**: Team security awareness
5. **Incident Drills**: Regular incident response practice

### Data Security

1. **Data Classification**: Categorize data sensitivity
2. **Data Loss Prevention**: Monitor data movement
3. **Backup Encryption**: Encrypt all backups
4. **Data Retention**: Implement retention policies
5. **Data Destruction**: Secure data deletion

## 📋 Security Checklist

### Pre-Deployment

- [ ] VPC configured with private subnets
- [ ] Security groups with minimal permissions
- [ ] IAM roles with least privilege
- [ ] KMS keys for encryption
- [ ] Secrets Manager for API keys
- [ ] CloudTrail enabled
- [ ] GuardDuty activated
- [ ] Backup strategy implemented

### Post-Deployment

- [ ] Security groups reviewed
- [ ] IAM permissions audited
- [ ] Encryption verified
- [ ] Monitoring configured
- [ ] Incident response tested
- [ ] Compliance validated
- [ ] Security training completed
- [ ] Documentation updated

## 🆘 Security Incident Response

### Immediate Response

1. **Isolate**: Isolate affected resources
2. **Assess**: Assess the scope of the incident
3. **Notify**: Notify relevant stakeholders
4. **Document**: Document all actions taken
5. **Preserve**: Preserve evidence for analysis

### Investigation

1. **Log Analysis**: Review all relevant logs
2. **Forensics**: Conduct forensic analysis
3. **Impact Assessment**: Determine impact scope
4. **Root Cause**: Identify root cause
5. **Timeline**: Create incident timeline

### Recovery

1. **Remediation**: Fix identified vulnerabilities
2. **Restoration**: Restore affected services
3. **Validation**: Validate system integrity
4. **Monitoring**: Enhanced monitoring
5. **Documentation**: Document lessons learned

## 📚 Security Resources

- [AWS Security Best Practices](https://aws.amazon.com/security/security-resources/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CIS Controls](https://www.cisecurity.org/controls/)
- [AWS Well-Architected Security Pillar](https://aws.amazon.com/architecture/well-architected/)
