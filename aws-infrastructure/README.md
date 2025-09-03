# AWS Infrastructure for Nautilus Trader Arbitrage Tools

This directory contains the complete AWS infrastructure setup for deploying the Nautilus Trader arbitrage monitoring system to the cloud.

## 🏗️ Architecture Overview

The infrastructure is designed for:
- **High Availability**: Multi-AZ deployment with auto-scaling
- **Security**: VPC isolation, IAM roles, and secrets management
- **Monitoring**: CloudWatch logs, metrics, and alarms
- **Cost Optimization**: Spot instances and auto-scaling
- **Scalability**: Container-based deployment with ECS/Fargate

## 📁 Directory Structure

```
aws-infrastructure/
├── terraform/                 # Infrastructure as Code
│   ├── environments/         # Environment-specific configs
│   │   ├── dev/             # Development environment
│   │   ├── staging/         # Staging environment
│   │   └── prod/            # Production environment
│   ├── modules/             # Reusable Terraform modules
│   │   ├── networking/      # VPC, subnets, security groups
│   │   ├── compute/         # ECS, Fargate, ALB
│   │   ├── storage/         # S3, RDS, ElastiCache
│   │   ├── monitoring/      # CloudWatch, alarms
│   │   └── security/        # IAM, secrets, KMS
│   └── main.tf              # Main Terraform configuration
├── docker/                   # Container configurations
│   ├── Dockerfile           # Main application container
│   ├── docker-compose.yml   # Local development
│   └── docker-compose.prod.yml # Production setup
├── scripts/                  # Deployment and utility scripts
│   ├── deploy.sh            # Main deployment script
│   ├── setup-aws.sh         # AWS CLI and tools setup
│   └── backup.sh            # Data backup script
├── monitoring/               # Monitoring configurations
│   ├── cloudwatch/          # CloudWatch dashboards
│   ├── grafana/             # Grafana dashboards
│   └── prometheus/          # Prometheus configs
└── docs/                     # Documentation
    ├── DEPLOYMENT.md         # Deployment guide
    ├── MONITORING.md         # Monitoring setup
    └── TROUBLESHOOTING.md    # Common issues
```

## 🚀 Quick Start

### Prerequisites
- AWS CLI configured with appropriate permissions
- Terraform >= 1.0
- Docker and Docker Compose
- Python 3.11+

### 1. Setup AWS Environment
```bash
cd aws-infrastructure
./scripts/setup-aws.sh
```

### 2. Deploy Infrastructure
```bash
# Deploy to development
./scripts/deploy.sh dev

# Deploy to production
./scripts/deploy.sh prod
```

### 3. Deploy Application
```bash
# Build and push Docker images
docker build -t nautilus-arbitrage:latest .

# Deploy to ECS
aws ecs update-service --cluster nautilus-arbitrage --service arbitrage-monitor
```

## 🔧 Configuration

### Environment Variables
- **API Keys**: Stored in AWS Secrets Manager
- **Configuration**: Environment-specific Terraform variables
- **Monitoring**: CloudWatch and custom metrics

### Scaling Configuration
- **Auto Scaling**: Based on CPU/memory usage
- **Spot Instances**: For cost optimization
- **Multi-AZ**: High availability across availability zones

## 📊 Monitoring

- **CloudWatch**: Logs, metrics, and alarms
- **Grafana**: Custom dashboards for trading metrics
- **Prometheus**: Application metrics collection
- **Alerting**: Slack/email notifications for critical events

## 🔒 Security

- **VPC**: Isolated network environment
- **IAM**: Least privilege access
- **Secrets Manager**: Secure API key storage
- **KMS**: Encryption at rest and in transit
- **WAF**: Web application firewall

## 💰 Cost Optimization

- **Spot Instances**: Up to 90% cost savings
- **Auto Scaling**: Scale down during low usage
- **S3 Lifecycle**: Automatic data archival
- **Reserved Instances**: For predictable workloads

## 📚 Documentation

- [Deployment Guide](docs/DEPLOYMENT.md)
- [Monitoring Setup](docs/MONITORING.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)

## 🆘 Support

For issues and questions:
1. Check the troubleshooting guide
2. Review CloudWatch logs
3. Check Terraform state
4. Contact the development team
