#!/bin/bash

# Simple AWS Deployment Script for Nautilus Trader Arbitrage
# This script deploys a minimal, working system in minutes

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
AWS_REGION="us-east-1"
PROJECT_NAME="nautilus-arbitrage"
ENVIRONMENT="prod"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    if ! command -v aws &> /dev/null; then
        log_error "AWS CLI not found. Please install it first."
        exit 1
    fi
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker not found. Please install it first."
        exit 1
    fi
    
    # Test AWS connection
    if ! aws sts get-caller-identity &> /dev/null; then
        log_error "AWS credentials not configured. Run 'aws configure' first."
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

# Create ECR repository
create_ecr_repo() {
    log_info "Creating ECR repository..."
    
    aws ecr create-repository \
        --repository-name "$PROJECT_NAME" \
        --region "$AWS_REGION" \
        --image-scanning-configuration scanOnPush=true \
        2>/dev/null || log_warning "ECR repository already exists"
    
    log_success "ECR repository ready"
}

# Build frontend
build_frontend() {
    log_info "Building React frontend..."
    
    # Build frontend
    "$PROJECT_ROOT/aws-infrastructure/scripts/build-frontend.sh"
    
    log_success "Frontend build completed"
}

# Build and push Docker image
build_and_push_image() {
    log_info "Building and pushing Docker image..."
    
    # Build frontend first
    build_frontend
    
    # Get ECR login token
    aws ecr get-login-password --region "$AWS_REGION" | docker login --username AWS --password-stdin "$(aws sts get-caller-identity --query Account --output text).dkr.ecr.$AWS_REGION.amazonaws.com"
    
    # Build image (from project root)
    cd "$PROJECT_ROOT"
    docker build -f aws-infrastructure/docker/Dockerfile -t "$PROJECT_NAME:latest" .
    
    # Tag and push
    ECR_URI="$(aws sts get-caller-identity --query Account --output text).dkr.ecr.$AWS_REGION.amazonaws.com/$PROJECT_NAME:latest"
    docker tag "$PROJECT_NAME:latest" "$ECR_URI"
    docker push "$ECR_URI"
    
    log_success "Docker image pushed to ECR"
}

# Create minimal infrastructure
create_infrastructure() {
    log_info "Creating minimal infrastructure..."
    
    # Create VPC (simple one)
    VPC_ID=$(aws ec2 create-vpc \
        --cidr-block 10.0.0.0/16 \
        --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value='$PROJECT_NAME'-vpc},{Key=Environment,Value='$ENVIRONMENT'}]' \
        --query 'Vpc.VpcId' \
        --output text \
        --region "$AWS_REGION")
    
    # Enable DNS
    aws ec2 modify-vpc-attribute --vpc-id "$VPC_ID" --enable-dns-hostnames --region "$AWS_REGION"
    aws ec2 modify-vpc-attribute --vpc-id "$VPC_ID" --enable-dns-support --region "$AWS_REGION"
    
    # Create public subnet
    SUBNET_ID=$(aws ec2 create-subnet \
        --vpc-id "$VPC_ID" \
        --cidr-block 10.0.1.0/24 \
        --availability-zone "${AWS_REGION}a" \
        --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value='$PROJECT_NAME'-public-subnet},{Key=Environment,Value='$ENVIRONMENT'}]' \
        --query 'Subnet.SubnetId' \
        --output text \
        --region "$AWS_REGION")
    
    # Create internet gateway
    IGW_ID=$(aws ec2 create-internet-gateway \
        --tag-specifications 'ResourceType=internet-gateway,Tags=[{Key=Name,Value='$PROJECT_NAME'-igw},{Key=Environment,Value='$ENVIRONMENT'}]' \
        --query 'InternetGateway.InternetGatewayId' \
        --output text \
        --region "$AWS_REGION")
    
    aws ec2 attach-internet-gateway --vpc-id "$VPC_ID" --internet-gateway-id "$IGW_ID" --region "$AWS_REGION"
    
    # Create route table
    RT_ID=$(aws ec2 create-route-table \
        --vpc-id "$VPC_ID" \
        --tag-specifications 'ResourceType=route-table,Tags=[{Key=Name,Value='$PROJECT_NAME'-rt},{Key=Environment,Value='$ENVIRONMENT'}]' \
        --query 'RouteTable.RouteTableId' \
        --output text \
        --region "$AWS_REGION")
    
    aws ec2 create-route --route-table-id "$RT_ID" --destination-cidr-block 0.0.0.0/0 --gateway-id "$IGW_ID" --region "$AWS_REGION"
    aws ec2 associate-route-table --subnet-id "$SUBNET_ID" --route-table-id "$RT_ID" --region "$AWS_REGION"
    
    # Create security group
    SG_ID=$(aws ec2 create-security-group \
        --group-name "$PROJECT_NAME-sg" \
        --description "Security group for $PROJECT_NAME" \
        --vpc-id "$VPC_ID" \
        --tag-specifications 'ResourceType=security-group,Tags=[{Key=Name,Value='$PROJECT_NAME'-sg},{Key=Environment,Value='$ENVIRONMENT'}]' \
        --query 'GroupId' \
        --output text \
        --region "$AWS_REGION")
    
    # Allow HTTP/HTTPS traffic from anywhere (for frontend)
    aws ec2 authorize-security-group-ingress --group-id "$SG_ID" --protocol tcp --port 80 --cidr 0.0.0.0/0 --region "$AWS_REGION"
    aws ec2 authorize-security-group-ingress --group-id "$SG_ID" --protocol tcp --port 443 --cidr 0.0.0.0/0 --region "$AWS_REGION"
    
    # Allow backend API (port 8000) only from localhost/same instance (internal only)
    aws ec2 authorize-security-group-ingress --group-id "$SG_ID" --protocol tcp --port 8000 --cidr 127.0.0.1/32 --region "$AWS_REGION"
    aws ec2 authorize-security-group-ingress --group-id "$SG_ID" --protocol tcp --port 8000 --cidr 10.0.1.0/24 --region "$AWS_REGION"
    
    # Create ECS cluster
    aws ecs create-cluster \
        --cluster-name "$PROJECT_NAME-cluster" \
        --tags key=Environment,value="$ENVIRONMENT" key=Name,value="$PROJECT_NAME-cluster" \
        --region "$AWS_REGION" \
        2>/dev/null || log_warning "ECS cluster already exists"
    
    log_success "Infrastructure created"
    
    # Save IDs for later use
    echo "VPC_ID=$VPC_ID" > .aws-resources
    echo "SUBNET_ID=$SUBNET_ID" >> .aws-resources
    echo "SG_ID=$SG_ID" >> .aws-resources
    echo "ECR_URI=$(aws sts get-caller-identity --query Account --output text).dkr.ecr.$AWS_REGION.amazonaws.com/$PROJECT_NAME:latest" >> .aws-resources
}

# Deploy application
deploy_application() {
    log_info "Deploying application to ECS..."
    
    source .aws-resources
    
    # Create task definition
    cat > task-definition.json << EOF
{
  "family": "$PROJECT_NAME-task",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "executionRoleArn": "arn:aws:iam::$(aws sts get-caller-identity --query Account --output text):role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "$PROJECT_NAME-container",
      "image": "$ECR_URI",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "essential": true,
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/$PROJECT_NAME",
          "awslogs-region": "$AWS_REGION",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "environment": [
        {
          "name": "ENVIRONMENT",
          "value": "$ENVIRONMENT"
        },
        {
          "name": "AWS_REGION",
          "value": "$AWS_REGION"
        }
      ]
    }
  ]
}
EOF
    
    # Create log group
    aws logs create-log-group \
        --log-group-name "/ecs/$PROJECT_NAME" \
        --region "$AWS_REGION" \
        2>/dev/null || log_warning "Log group already exists"
    
    # Register task definition
    aws ecs register-task-definition \
        --cli-input-json file://task-definition.json \
        --region "$AWS_REGION"
    
    # Create service
    aws ecs create-service \
        --cluster "$PROJECT_NAME-cluster" \
        --service-name "$PROJECT_NAME-service" \
        --task-definition "$PROJECT_NAME-task" \
        --desired-count 1 \
        --launch-type FARGATE \
        --network-configuration "awsvpcConfiguration={subnets=[$SUBNET_ID],securityGroups=[$SG_ID],assignPublicIp=ENABLED}" \
        --region "$AWS_REGION" \
        2>/dev/null || log_warning "ECS service already exists"
    
    log_success "Application deployed to ECS"
}

# Get application URL
get_application_url() {
    log_info "Getting application URL..."
    
    source .aws-resources
    
    # Get public IP
    TASK_ARN=$(aws ecs list-tasks \
        --cluster "$PROJECT_NAME-cluster" \
        --service-name "$PROJECT_NAME-service" \
        --query 'taskArns[0]' \
        --output text \
        --region "$AWS_REGION")
    
    if [ "$TASK_ARN" != "None" ] && [ "$TASK_ARN" != "null" ]; then
        ENI_ID=$(aws ecs describe-tasks \
            --cluster "$PROJECT_NAME-cluster" \
            --tasks "$TASK_ARN" \
            --query 'tasks[0].attachments[0].details[?name==`networkInterfaceId`].value' \
            --output text \
            --region "$AWS_REGION")
        
        PUBLIC_IP=$(aws ec2 describe-network-interfaces \
            --network-interface-ids "$ENI_ID" \
            --query 'NetworkInterfaces[0].Association.PublicIp' \
            --output text \
            --region "$AWS_REGION")
        
        log_success "Application is running at: http://$PUBLIC_IP:8000"
        log_info "Health check: http://$PUBLIC_IP:8000/health"
        log_info "API endpoints: http://$PUBLIC_IP:8000/api/*"
    else
        log_warning "No running tasks found. Check ECS console for status."
    fi
}

# Main deployment
main() {
    log_info "Starting simple deployment to AWS..."
    
    check_prerequisites
    create_ecr_repo
    build_and_push_image
    create_infrastructure
    deploy_application
    
    log_success "Deployment completed!"
    get_application_url
    
    log_info "Next steps:"
    log_info "1. Update your API keys in AWS Secrets Manager"
    log_info "2. Access the application at the URL above"
    log_info "3. Use the frontend to configure your trading parameters"
}

# Run main function
main "$@"
