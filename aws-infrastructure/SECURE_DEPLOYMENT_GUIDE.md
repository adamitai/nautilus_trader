# Secure Deployment Guide - Nautilus Trader Arbitrage Tools

## 🔐 **IMPORTANT: Never Share Your API Keys**

**Your trading API keys are extremely sensitive and should NEVER be shared with anyone, including AI assistants.**

## 🚀 Quick Start (Secure Method)

### Step 1: Setup Your Environment

```bash
# 1. Run the setup script
./aws-infrastructure/scripts/setup-aws.sh

# 2. Configure AWS CLI
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key  
# Enter your preferred region (e.g., us-west-2)
# Enter output format (json)
```

### Step 2: Store Your API Keys Securely

**Option A: Using AWS Secrets Manager (Recommended)**

```bash
# Create a secure secret with your API keys
aws secretsmanager create-secret \
    --name "nautilus-arbitrage-dev-api-keys" \
    --description "API keys for cryptocurrency exchanges" \
    --secret-string '{
        "BINANCE_API_KEY": "YOUR_ACTUAL_BINANCE_API_KEY",
        "BINANCE_API_SECRET": "YOUR_ACTUAL_BINANCE_SECRET",
        "BYBIT_API_KEY": "YOUR_ACTUAL_BYBIT_API_KEY", 
        "BYBIT_API_SECRET": "YOUR_ACTUAL_BYBIT_SECRET",
        "OKX_API_KEY": "YOUR_ACTUAL_OKX_API_KEY",
        "OKX_API_SECRET": "YOUR_ACTUAL_OKX_SECRET",
        "OKX_PASSPHRASE": "YOUR_ACTUAL_OKX_PASSPHRASE"
    }'
```

**Option B: Using Environment Variables**

```bash
# Set environment variables (temporary for deployment)
export BINANCE_API_KEY="YOUR_ACTUAL_BINANCE_API_KEY"
export BINANCE_API_SECRET="YOUR_ACTUAL_BINANCE_SECRET"
export BYBIT_API_KEY="YOUR_ACTUAL_BYBIT_API_KEY"
export BYBIT_API_SECRET="YOUR_ACTUAL_BYBIT_SECRET"
export OKX_API_KEY="YOUR_ACTUAL_OKX_API_KEY"
export OKX_API_SECRET="YOUR_ACTUAL_OKX_SECRET"
export OKX_PASSPHRASE="YOUR_ACTUAL_OKX_PASSPHRASE"
```

### Step 3: Deploy to Development

```bash
# Deploy to development environment first
./aws-infrastructure/scripts/deploy.sh dev

# This will:
# 1. Create AWS infrastructure (VPC, RDS, ECS, etc.)
# 2. Build and push Docker image
# 3. Deploy application to ECS
# 4. Setup monitoring and alerting
```

### Step 4: Verify Deployment

```bash
# Check service status
aws ecs describe-services \
    --cluster nautilus-arbitrage-dev-cluster \
    --services nautilus-arbitrage-dev-service

# View logs
aws logs tail /ecs/nautilus-arbitrage-dev --follow

# Get load balancer URL
aws elbv2 describe-load-balancers \
    --names nautilus-arbitrage-dev-alb \
    --query 'LoadBalancers[0].DNSName'
```

### Step 5: Deploy to Production (When Ready)

```bash
# Deploy to production
./aws-infrastructure/scripts/deploy.sh prod
```

## 🏗️ What Gets Deployed

### Infrastructure Components

1. **VPC Network**
   - Private subnets for application
   - Public subnets for load balancer
   - Database subnets for RDS
   - NAT Gateway for outbound access

2. **Compute (ECS Fargate)**
   - Containerized application
   - Auto-scaling based on CPU/memory
   - Health checks and monitoring

3. **Database (RDS PostgreSQL)**
   - Encrypted at rest and in transit
   - Automated backups
   - Performance monitoring

4. **Cache (ElastiCache Redis)**
   - In-memory data store
   - High availability setup
   - Automatic failover

5. **Load Balancer (ALB)**
   - HTTPS termination
   - Health checks
   - SSL certificates

6. **Monitoring (CloudWatch)**
   - Application metrics
   - Log aggregation
   - Custom dashboards
   - Automated alerts

### Security Features

- **Encryption**: All data encrypted with KMS
- **Secrets Management**: API keys stored securely
- **Network Isolation**: Private subnets only
- **IAM Roles**: Least privilege access
- **VPC Endpoints**: Private AWS service access

## 📊 Monitoring Your Deployment

### CloudWatch Dashboard

Access your dashboard at:
```
https://us-west-2.console.aws.amazon.com/cloudwatch/home?region=us-west-2#dashboards:name=nautilus-arbitrage-dev-dashboard
```

### Key Metrics to Monitor

1. **Application Health**
   - ECS service status
   - Task count and health
   - Response times

2. **Trading Performance**
   - Arbitrage opportunities detected
   - Trading errors
   - Profit/loss metrics

3. **System Resources**
   - CPU and memory usage
   - Database connections
   - Cache hit rates

4. **Exchange Connectivity**
   - API response times
   - Error rates
   - Connection status

## 🔧 Configuration Options

### Environment-Specific Settings

**Development (`dev`):**
- Smaller instances (t3.micro)
- Single database instance
- Basic monitoring
- Lower costs

**Production (`prod`):**
- Larger instances (t3.large)
- Multi-AZ database
- Enhanced monitoring
- High availability

### Customization

Edit these files to customize your deployment:

- `aws-infrastructure/terraform/environments/dev/terraform.tfvars`
- `aws-infrastructure/terraform/environments/prod/terraform.tfvars`

## 🚨 Important Security Notes

### API Key Security

1. **Never commit API keys to git**
2. **Use AWS Secrets Manager for production**
3. **Rotate keys regularly**
4. **Monitor key usage**
5. **Use read-only keys when possible**

### Network Security

1. **Application runs in private subnets**
2. **No direct internet access**
3. **All traffic encrypted**
4. **Firewall rules restrictive**

### Access Control

1. **IAM roles with minimal permissions**
2. **No long-term access keys**
3. **MFA enabled for AWS console**
4. **Regular access reviews**

## 💰 Cost Optimization

### Development Environment
- **Estimated Cost**: $50-100/month
- **Components**: t3.micro instances, basic RDS, minimal storage

### Production Environment  
- **Estimated Cost**: $200-500/month
- **Components**: t3.large instances, multi-AZ RDS, enhanced monitoring

### Cost Optimization Tips

1. **Use Spot Instances**: Up to 90% savings
2. **Auto-scaling**: Scale down during low usage
3. **Reserved Instances**: For predictable workloads
4. **S3 Lifecycle**: Automatic data archival

## 🆘 Getting Help

### Common Issues

1. **Service won't start**: Check logs and resource limits
2. **Database connection fails**: Verify security groups
3. **API key errors**: Check Secrets Manager permissions
4. **High costs**: Review instance sizes and usage

### Support Resources

- **Documentation**: `aws-infrastructure/docs/`
- **Troubleshooting**: `aws-infrastructure/docs/TROUBLESHOOTING.md`
- **Security Guide**: `aws-infrastructure/docs/SECURITY.md`
- **AWS Support**: For infrastructure issues

## ✅ Deployment Checklist

### Pre-Deployment
- [ ] AWS CLI configured
- [ ] API keys secured in Secrets Manager
- [ ] Terraform and Docker installed
- [ ] AWS permissions verified

### During Deployment
- [ ] Development environment deployed
- [ ] Application logs reviewed
- [ ] Health checks passing
- [ ] Monitoring configured

### Post-Deployment
- [ ] Production environment deployed
- [ ] Alerts configured
- [ ] Backup strategy implemented
- [ ] Team access configured

## 🎯 Next Steps

1. **Deploy to development** and test thoroughly
2. **Monitor performance** and adjust resources
3. **Configure alerts** for critical events
4. **Deploy to production** when ready
5. **Set up regular backups** and maintenance

---

**Remember: Your API keys are your responsibility. Keep them secure and never share them with anyone.**
