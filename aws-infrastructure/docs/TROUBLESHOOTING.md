# Troubleshooting Guide - Nautilus Trader Arbitrage Tools

This guide helps you diagnose and resolve common issues with the Nautilus Trader arbitrage monitoring system deployed on AWS.

## 🔍 Diagnostic Tools

### AWS CLI Commands

```bash
# Check ECS service status
aws ecs describe-services \
    --cluster nautilus-arbitrage-dev-cluster \
    --services nautilus-arbitrage-dev-service

# View recent logs
aws logs tail /ecs/nautilus-arbitrage-dev --follow

# Check RDS status
aws rds describe-db-instances \
    --db-instance-identifier nautilus-arbitrage-dev-db

# Verify load balancer health
aws elbv2 describe-target-health \
    --target-group-arn <target-group-arn>
```

### Terraform Commands

```bash
# Check Terraform state
terraform show
terraform plan

# Validate configuration
terraform validate

# Check resource status
terraform state list
terraform state show <resource-name>
```

## 🚨 Common Issues and Solutions

### 1. ECS Service Won't Start

**Symptoms:**
- Service shows "PENDING" status
- Tasks fail to start
- No running tasks

**Diagnosis:**
```bash
# Check service events
aws ecs describe-services \
    --cluster nautilus-arbitrage-dev-cluster \
    --services nautilus-arbitrage-dev-service \
    --query 'services[0].events'

# Check task definition
aws ecs describe-task-definition \
    --task-definition nautilus-arbitrage-dev

# Check task failures
aws ecs list-tasks \
    --cluster nautilus-arbitrage-dev-cluster \
    --service-name nautilus-arbitrage-dev-service \
    --desired-status STOPPED
```

**Common Causes:**
- **Insufficient Resources**: CPU/memory limits too low
- **Image Pull Errors**: Docker image not found
- **Health Check Failures**: Application not responding
- **Network Issues**: Security group or subnet problems

**Solutions:**
```bash
# Increase task resources
# Update terraform variables:
container_cpu = 1024
container_memory = 2048

# Check Docker image exists
aws ecr describe-images \
    --repository-name nautilus-arbitrage \
    --image-ids imageTag=dev

# Verify health check endpoint
curl -f http://localhost:8000/health
```

### 2. Database Connection Issues

**Symptoms:**
- Application logs show connection errors
- Database queries timeout
- RDS instance unreachable

**Diagnosis:**
```bash
# Check RDS status
aws rds describe-db-instances \
    --db-instance-identifier nautilus-arbitrage-dev-db \
    --query 'DBInstances[0].DBInstanceStatus'

# Test database connectivity
aws rds describe-db-instances \
    --db-instance-identifier nautilus-arbitrage-dev-db \
    --query 'DBInstances[0].Endpoint'

# Check security groups
aws ec2 describe-security-groups \
    --group-ids <rds-security-group-id>
```

**Common Causes:**
- **Security Group Rules**: Port 5432 not open
- **Subnet Issues**: Database in wrong subnet
- **Parameter Group**: Incorrect database settings
- **Storage Issues**: Database out of space

**Solutions:**
```bash
# Update security group
aws ec2 authorize-security-group-ingress \
    --group-id <rds-security-group-id> \
    --protocol tcp \
    --port 5432 \
    --source-group <ecs-security-group-id>

# Check database storage
aws rds describe-db-instances \
    --db-instance-identifier nautilus-arbitrage-dev-db \
    --query 'DBInstances[0].AllocatedStorage'

# Modify database if needed
aws rds modify-db-instance \
    --db-instance-identifier nautilus-arbitrage-dev-db \
    --allocated-storage 50
```

### 3. API Key Authentication Failures

**Symptoms:**
- Exchange API calls fail
- Authentication errors in logs
- Trading operations not working

**Diagnosis:**
```bash
# Check secrets manager
aws secretsmanager get-secret-value \
    --secret-id nautilus-arbitrage-dev-api-keys

# Verify IAM permissions
aws iam get-role-policy \
    --role-name nautilus-arbitrage-dev-ecs-task-role \
    --policy-name nautilus-arbitrage-dev-secrets-manager-policy

# Test API key access
aws secretsmanager get-secret-value \
    --secret-id nautilus-arbitrage-dev-api-keys \
    --query 'SecretString' \
    --output text | jq '.BINANCE_API_KEY'
```

**Common Causes:**
- **Invalid API Keys**: Keys expired or incorrect
- **IAM Permissions**: Task role can't access secrets
- **Key Format**: Incorrect JSON format in secrets
- **Exchange Issues**: Exchange API problems

**Solutions:**
```bash
# Update API keys
aws secretsmanager update-secret \
    --secret-id nautilus-arbitrage-dev-api-keys \
    --secret-string '{
        "BINANCE_API_KEY": "new_key",
        "BINANCE_API_SECRET": "new_secret"
    }'

# Verify IAM policy
aws iam attach-role-policy \
    --role-name nautilus-arbitrage-dev-ecs-task-role \
    --policy-arn arn:aws:iam::aws:policy/SecretsManagerReadWrite

# Test exchange connectivity
curl -X GET "https://api.binance.com/api/v3/ping"
```

### 4. Load Balancer Health Check Failures

**Symptoms:**
- Targets showing unhealthy
- 502/503 errors from load balancer
- Application not accessible

**Diagnosis:**
```bash
# Check target health
aws elbv2 describe-target-health \
    --target-group-arn <target-group-arn>

# Check load balancer logs
aws logs describe-log-groups \
    --log-group-name-prefix /aws/applicationloadbalancer

# Test health endpoint
curl -f http://<load-balancer-dns>/health
```

**Common Causes:**
- **Health Check Path**: Incorrect health check endpoint
- **Port Mismatch**: Health check on wrong port
- **Security Groups**: Load balancer can't reach targets
- **Application Issues**: Health endpoint not responding

**Solutions:**
```bash
# Update health check
aws elbv2 modify-target-group \
    --target-group-arn <target-group-arn> \
    --health-check-path /health \
    --health-check-port 8000 \
    --health-check-protocol HTTP

# Check security groups
aws ec2 describe-security-groups \
    --group-ids <ecs-security-group-id>

# Test application directly
docker run -p 8000:8000 nautilus-arbitrage:dev
curl http://localhost:8000/health
```

### 5. High Memory/CPU Usage

**Symptoms:**
- Tasks being killed due to memory limits
- High CPU utilization
- Slow response times

**Diagnosis:**
```bash
# Check CloudWatch metrics
aws cloudwatch get-metric-statistics \
    --namespace AWS/ECS \
    --metric-name MemoryUtilization \
    --dimensions Name=ServiceName,Value=nautilus-arbitrage-dev-service \
    --start-time 2024-01-01T00:00:00Z \
    --end-time 2024-01-01T23:59:59Z \
    --period 300 \
    --statistics Average

# Check container logs
aws logs filter-log-events \
    --log-group-name /ecs/nautilus-arbitrage-dev \
    --filter-pattern "memory"
```

**Common Causes:**
- **Memory Leaks**: Application not releasing memory
- **Inefficient Code**: Poor algorithm performance
- **Large Data Sets**: Processing too much data
- **Resource Limits**: Container limits too low

**Solutions:**
```bash
# Increase container resources
# Update terraform variables:
container_cpu = 2048
container_memory = 4096

# Enable auto-scaling
aws application-autoscaling register-scalable-target \
    --service-namespace ecs \
    --resource-id service/nautilus-arbitrage-dev-cluster/nautilus-arbitrage-dev-service \
    --scalable-dimension ecs:service:DesiredCount \
    --min-capacity 2 \
    --max-capacity 10

# Optimize application code
# Review memory usage patterns
# Implement connection pooling
# Use streaming for large datasets
```

## 📊 Monitoring and Alerting Issues

### 1. CloudWatch Alarms Not Triggering

**Symptoms:**
- Alarms not firing when expected
- Missing notifications
- Incorrect alarm states

**Diagnosis:**
```bash
# Check alarm configuration
aws cloudwatch describe-alarms \
    --alarm-names nautilus-arbitrage-dev-ecs-high-cpu

# Check alarm history
aws cloudwatch describe-alarm-history \
    --alarm-name nautilus-arbitrage-dev-ecs-high-cpu \
    --start-date 2024-01-01T00:00:00Z

# Verify SNS topic
aws sns get-topic-attributes \
    --topic-arn <sns-topic-arn>
```

**Solutions:**
```bash
# Update alarm thresholds
aws cloudwatch put-metric-alarm \
    --alarm-name nautilus-arbitrage-dev-ecs-high-cpu \
    --alarm-description "ECS CPU utilization" \
    --metric-name CPUUtilization \
    --namespace AWS/ECS \
    --statistic Average \
    --period 300 \
    --threshold 80 \
    --comparison-operator GreaterThanThreshold \
    --evaluation-periods 2

# Test SNS notification
aws sns publish \
    --topic-arn <sns-topic-arn> \
    --message "Test notification"
```

### 2. Log Aggregation Issues

**Symptoms:**
- Logs not appearing in CloudWatch
- Missing log streams
- Incomplete log data

**Diagnosis:**
```bash
# Check log groups
aws logs describe-log-groups \
    --log-group-name-prefix /ecs/nautilus-arbitrage

# Check log streams
aws logs describe-log-streams \
    --log-group-name /ecs/nautilus-arbitrage-dev

# Check log events
aws logs get-log-events \
    --log-group-name /ecs/nautilus-arbitrage-dev \
    --log-stream-name <log-stream-name>
```

**Solutions:**
```bash
# Create log group if missing
aws logs create-log-group \
    --log-group-name /ecs/nautilus-arbitrage-dev

# Set retention policy
aws logs put-retention-policy \
    --log-group-name /ecs/nautilus-arbitrage-dev \
    --retention-in-days 30

# Check IAM permissions
aws iam get-role-policy \
    --role-name nautilus-arbitrage-dev-ecs-task-execution-role \
    --policy-name nautilus-arbitrage-dev-ecs-task-execution-policy
```

## 🔧 Performance Issues

### 1. Slow Database Queries

**Symptoms:**
- High database CPU usage
- Slow query response times
- Connection timeouts

**Diagnosis:**
```bash
# Check RDS performance insights
aws rds describe-db-instances \
    --db-instance-identifier nautilus-arbitrage-dev-db \
    --query 'DBInstances[0].PerformanceInsightsEnabled'

# Check slow query log
aws rds describe-db-instances \
    --db-instance-identifier nautilus-arbitrage-dev-db \
    --query 'DBInstances[0].EnabledCloudwatchLogsExports'
```

**Solutions:**
```bash
# Enable Performance Insights
aws rds modify-db-instance \
    --db-instance-identifier nautilus-arbitrage-dev-db \
    --enable-performance-insights \
    --performance-insights-retention-period 7

# Enable slow query log
aws rds modify-db-instance \
    --db-instance-identifier nautilus-arbitrage-dev-db \
    --enable-cloudwatch-logs-exports postgresql

# Add database indexes
# Review query performance
# Implement connection pooling
```

### 2. Redis Cache Issues

**Symptoms:**
- High cache miss rates
- Slow cache operations
- Memory usage issues

**Diagnosis:**
```bash
# Check ElastiCache metrics
aws cloudwatch get-metric-statistics \
    --namespace AWS/ElastiCache \
    --metric-name CacheHits \
    --dimensions Name=CacheClusterId,Value=nautilus-arbitrage-dev-cache \
    --start-time 2024-01-01T00:00:00Z \
    --end-time 2024-01-01T23:59:59Z \
    --period 300 \
    --statistics Sum
```

**Solutions:**
```bash
# Optimize cache configuration
# Review cache key patterns
# Implement cache warming
# Monitor cache hit rates
```

## 🚨 Emergency Procedures

### 1. Service Recovery

```bash
# Restart ECS service
aws ecs update-service \
    --cluster nautilus-arbitrage-dev-cluster \
    --service nautilus-arbitrage-dev-service \
    --force-new-deployment

# Scale up service
aws ecs update-service \
    --cluster nautilus-arbitrage-dev-cluster \
    --service nautilus-arbitrage-dev-service \
    --desired-count 3
```

### 2. Database Recovery

```bash
# Create database snapshot
aws rds create-db-snapshot \
    --db-instance-identifier nautilus-arbitrage-dev-db \
    --db-snapshot-identifier nautilus-arbitrage-dev-emergency-backup

# Restore from snapshot
aws rds restore-db-instance-from-db-snapshot \
    --db-instance-identifier nautilus-arbitrage-dev-db-restored \
    --db-snapshot-identifier nautilus-arbitrage-dev-emergency-backup
```

### 3. Rollback Procedures

```bash
# Rollback to previous task definition
aws ecs update-service \
    --cluster nautilus-arbitrage-dev-cluster \
    --service nautilus-arbitrage-dev-service \
    --task-definition nautilus-arbitrage-dev:previous

# Rollback Terraform changes
cd aws-infrastructure/terraform
terraform plan -target=aws_ecs_service.main
terraform apply -target=aws_ecs_service.main
```

## 📞 Getting Help

### Internal Resources

1. **Check Documentation**: Review deployment and security guides
2. **Review Logs**: Analyze CloudWatch logs and application logs
3. **Check Metrics**: Review CloudWatch dashboards
4. **Verify Configuration**: Check Terraform state and resources

### External Resources

1. **AWS Support**: For AWS service issues
2. **Nautilus Trader Documentation**: For application-specific issues
3. **Community Forums**: For general troubleshooting
4. **Professional Services**: For complex issues

### Escalation Process

1. **Level 1**: Check logs and basic diagnostics
2. **Level 2**: Review configuration and metrics
3. **Level 3**: Engage AWS support or professional services
4. **Level 4**: Escalate to development team

## 📋 Troubleshooting Checklist

### Pre-Troubleshooting

- [ ] Verify AWS credentials and permissions
- [ ] Check service status in AWS console
- [ ] Review recent changes and deployments
- [ ] Gather relevant logs and metrics
- [ ] Document symptoms and error messages

### During Troubleshooting

- [ ] Isolate the problem scope
- [ ] Check multiple sources of information
- [ ] Test hypotheses systematically
- [ ] Document findings and actions
- [ ] Implement fixes incrementally

### Post-Troubleshooting

- [ ] Verify fix effectiveness
- [ ] Update monitoring and alerting
- [ ] Document root cause and solution
- [ ] Implement preventive measures
- [ ] Share knowledge with team
