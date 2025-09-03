# Deployment Guide - Nautilus Trader Arbitrage Tools

This guide walks you through deploying the Nautilus Trader arbitrage monitoring system to AWS.

## 📋 Prerequisites

Before deploying, ensure you have:

1. **AWS Account** with appropriate permissions
2. **AWS CLI** configured with credentials
3. **Terraform** >= 1.0 installed
4. **Docker** and Docker Compose installed
5. **API Keys** for cryptocurrency exchanges (Binance, Bybit, OKX)

## 🚀 Quick Start

### 1. Setup AWS Environment

```bash
# Run the setup script to install required tools
./aws-infrastructure/scripts/setup-aws.sh

# Configure AWS CLI (if not already done)
aws configure
```

### 2. Configure API Keys

**Option A: Using AWS Secrets Manager (Recommended)**

```bash
# Create secrets in AWS Secrets Manager
aws secretsmanager create-secret \
    --name "nautilus-arbitrage-dev-api-keys" \
    --description "API keys for cryptocurrency exchanges" \
    --secret-string '{
        "BINANCE_API_KEY": "your_binance_api_key",
        "BINANCE_API_SECRET": "your_binance_secret",
        "BYBIT_API_KEY": "your_bybit_api_key",
        "BYBIT_API_SECRET": "your_bybit_secret",
        "OKX_API_KEY": "your_okx_api_key",
        "OKX_API_SECRET": "your_okx_secret",
        "OKX_PASSPHRASE": "your_okx_passphrase"
    }'
```

**Option B: Using Environment Variables**

```bash
export BINANCE_API_KEY="your_binance_api_key"
export BINANCE_API_SECRET="your_binance_secret"
export BYBIT_API_KEY="your_bybit_api_key"
export BYBIT_API_SECRET="your_bybit_secret"
export OKX_API_KEY="your_okx_api_key"
export OKX_API_SECRET="your_okx_secret"
export OKX_PASSPHRASE="your_okx_passphrase"
```

### 3. Deploy Infrastructure

```bash
# Deploy to development environment
./aws-infrastructure/scripts/deploy.sh dev

# Deploy to production environment
./aws-infrastructure/scripts/deploy.sh prod
```

## 🔧 Detailed Deployment Steps

### Step 1: Infrastructure Setup

The deployment script will:

1. **Create S3 bucket** for Terraform state storage
2. **Deploy VPC** with public/private subnets
3. **Create security groups** and IAM roles
4. **Deploy RDS** PostgreSQL database
5. **Deploy ElastiCache** Redis cluster
6. **Create ECS cluster** with Fargate
7. **Deploy Application Load Balancer**
8. **Setup CloudWatch** monitoring and alarms

### Step 2: Application Deployment

1. **Build Docker image** with your application
2. **Push to ECR** (Elastic Container Registry)
3. **Deploy to ECS** with auto-scaling
4. **Configure health checks** and monitoring

### Step 3: Verification

After deployment, verify:

```bash
# Check ECS service status
aws ecs describe-services \
    --cluster nautilus-arbitrage-dev-cluster \
    --services nautilus-arbitrage-dev-service

# View application logs
aws logs tail /ecs/nautilus-arbitrage-dev --follow

# Check load balancer health
aws elbv2 describe-target-health \
    --target-group-arn <target-group-arn>
```

## 🌍 Environment-Specific Configurations

### Development Environment

- **Instance Type**: t3.micro
- **Database**: db.t3.micro
- **Cache**: cache.t3.micro
- **Min Capacity**: 1 task
- **Max Capacity**: 3 tasks

### Production Environment

- **Instance Type**: t3.large
- **Database**: db.r6g.large
- **Cache**: cache.r6g.large
- **Min Capacity**: 2 tasks
- **Max Capacity**: 10 tasks

## 🔐 Security Configuration

### Network Security

- **VPC**: Isolated network environment
- **Private Subnets**: Application runs in private subnets
- **Security Groups**: Restrictive firewall rules
- **NAT Gateway**: Outbound internet access only

### Data Security

- **Encryption**: All data encrypted at rest and in transit
- **Secrets Manager**: API keys stored securely
- **IAM Roles**: Least privilege access
- **KMS**: Customer-managed encryption keys

### Access Control

- **IAM Policies**: Granular permissions
- **VPC Endpoints**: Private AWS service access
- **WAF**: Web application firewall (optional)

## 📊 Monitoring and Alerting

### CloudWatch Metrics

- **ECS**: CPU, memory, task count
- **RDS**: CPU, connections, storage
- **ElastiCache**: CPU, connections, evictions
- **ALB**: Response time, error rates

### Custom Metrics

- **Trading Errors**: Number of trading errors
- **Arbitrage Opportunities**: Opportunities detected
- **Exchange Connectivity**: API connection status
- **Profit/Loss**: Trading performance

### Alerts

- **High CPU/Memory**: Scale up resources
- **Database Issues**: Storage, connections
- **Trading Errors**: Critical failures
- **High Response Time**: Performance issues

## 🔄 Auto-Scaling Configuration

### ECS Auto Scaling

```hcl
# CPU-based scaling
target_tracking_scaling_policy_configuration {
  predefined_metric_specification {
    predefined_metric_type = "ECSServiceAverageCPUUtilization"
  }
  target_value = 70.0
}

# Memory-based scaling
target_tracking_scaling_policy_configuration {
  predefined_metric_specification {
    predefined_metric_type = "ECSServiceAverageMemoryUtilization"
  }
  target_value = 80.0
}
```

### Scaling Triggers

- **CPU Utilization** > 70%
- **Memory Utilization** > 80%
- **Request Count** > 1000/min
- **Response Time** > 2 seconds

## 🗄️ Database Configuration

### PostgreSQL Setup

```sql
-- Create database and user
CREATE DATABASE nautilus_arbitrage;
CREATE USER nautilus WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE nautilus_arbitrage TO nautilus;

-- Create tables for trading data
CREATE TABLE arbitrage_opportunities (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT NOW(),
    symbol VARCHAR(20) NOT NULL,
    exchange_buy VARCHAR(20) NOT NULL,
    exchange_sell VARCHAR(20) NOT NULL,
    price_buy DECIMAL(20,8) NOT NULL,
    price_sell DECIMAL(20,8) NOT NULL,
    spread_percent DECIMAL(8,4) NOT NULL,
    volume_usd DECIMAL(20,2) NOT NULL,
    profit_usd DECIMAL(20,2) NOT NULL
);

CREATE INDEX idx_arbitrage_timestamp ON arbitrage_opportunities(timestamp);
CREATE INDEX idx_arbitrage_symbol ON arbitrage_opportunities(symbol);
```

### Redis Configuration

```redis
# Cache configuration
maxmemory-policy allkeys-lru
timeout 300
tcp-keepalive 60

# Persistence
save 900 1
save 300 10
save 60 10000
```

## 🚨 Troubleshooting

### Common Issues

**1. ECS Service Won't Start**

```bash
# Check task definition
aws ecs describe-task-definition --task-definition nautilus-arbitrage-dev

# Check service events
aws ecs describe-services \
    --cluster nautilus-arbitrage-dev-cluster \
    --services nautilus-arbitrage-dev-service
```

**2. Database Connection Issues**

```bash
# Check RDS status
aws rds describe-db-instances --db-instance-identifier nautilus-arbitrage-dev-db

# Test connection
aws rds describe-db-instances \
    --db-instance-identifier nautilus-arbitrage-dev-db \
    --query 'DBInstances[0].Endpoint'
```

**3. API Key Issues**

```bash
# Check secrets manager
aws secretsmanager get-secret-value \
    --secret-id nautilus-arbitrage-dev-api-keys

# Verify IAM permissions
aws iam get-role-policy \
    --role-name nautilus-arbitrage-dev-ecs-task-role \
    --policy-name nautilus-arbitrage-dev-secrets-manager-policy
```

### Log Analysis

```bash
# View application logs
aws logs tail /ecs/nautilus-arbitrage-dev --follow

# Filter for errors
aws logs filter-log-events \
    --log-group-name /ecs/nautilus-arbitrage-dev \
    --filter-pattern "ERROR"

# Export logs for analysis
aws logs create-export-task \
    --log-group-name /ecs/nautilus-arbitrage-dev \
    --from-time $(date -d '1 hour ago' +%s)000 \
    --to-time $(date +%s)000 \
    --destination nautilus-arbitrage-dev-logs \
    --destination-prefix logs/
```

## 🔄 Updates and Maintenance

### Application Updates

```bash
# Update application code
git pull origin main

# Rebuild and deploy
./aws-infrastructure/scripts/deploy.sh dev --skip-terraform
```

### Infrastructure Updates

```bash
# Update Terraform configuration
cd aws-infrastructure/terraform
terraform plan
terraform apply
```

### Database Maintenance

```bash
# Create backup
aws rds create-db-snapshot \
    --db-instance-identifier nautilus-arbitrage-dev-db \
    --db-snapshot-identifier nautilus-arbitrage-dev-backup-$(date +%Y%m%d)

# Restore from backup
aws rds restore-db-instance-from-db-snapshot \
    --db-instance-identifier nautilus-arbitrage-dev-db-restored \
    --db-snapshot-identifier nautilus-arbitrage-dev-backup-20240101
```

## 📈 Performance Optimization

### Cost Optimization

- **Spot Instances**: Use Fargate Spot for non-critical workloads
- **Reserved Capacity**: For predictable workloads
- **Auto Scaling**: Scale down during low usage
- **S3 Lifecycle**: Automatic data archival

### Performance Tuning

- **Database**: Connection pooling, query optimization
- **Cache**: Redis clustering, memory optimization
- **Application**: Async processing, batch operations
- **Network**: VPC endpoints, CDN for static content

## 🆘 Support

For issues and questions:

1. **Check logs**: CloudWatch logs and application logs
2. **Review metrics**: CloudWatch dashboards
3. **Verify configuration**: Terraform state and resources
4. **Contact support**: Development team or AWS support

## 📚 Additional Resources

- [AWS ECS Documentation](https://docs.aws.amazon.com/ecs/)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [Nautilus Trader Documentation](https://nautilustrader.io/docs)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
