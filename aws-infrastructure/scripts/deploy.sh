#!/bin/bash

# Nautilus Trader Arbitrage Tools - Deployment Script
# This script deploys the complete infrastructure to AWS

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
TERRAFORM_DIR="$PROJECT_ROOT/aws-infrastructure/terraform"
DOCKER_DIR="$PROJECT_ROOT/aws-infrastructure/docker"

# Default values
ENVIRONMENT="dev"
AWS_REGION="us-west-2"
SKIP_BUILD=false
SKIP_TERRAFORM=false
SKIP_DOCKER=false
DRY_RUN=false

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

show_help() {
    cat << EOF
Nautilus Trader Arbitrage Tools - Deployment Script

USAGE:
    $0 [OPTIONS] ENVIRONMENT

ARGUMENTS:
    ENVIRONMENT    Target environment (dev, staging, prod)

OPTIONS:
    -h, --help              Show this help message
    -r, --region REGION     AWS region (default: us-west-2)
    --skip-build            Skip Docker image build
    --skip-terraform        Skip Terraform deployment
    --skip-docker           Skip Docker deployment
    --dry-run               Show what would be deployed without executing
    --auto-approve          Auto-approve Terraform changes

EXAMPLES:
    $0 dev                          # Deploy to development
    $0 prod --region us-east-1      # Deploy to production in us-east-1
    $0 staging --skip-build         # Deploy to staging without rebuilding
    $0 dev --dry-run                # Show what would be deployed

EOF
}

check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if required tools are installed
    local missing_tools=()
    
    if ! command -v aws &> /dev/null; then
        missing_tools+=("aws-cli")
    fi
    
    if ! command -v terraform &> /dev/null; then
        missing_tools+=("terraform")
    fi
    
    if ! command -v docker &> /dev/null; then
        missing_tools+=("docker")
    fi
    
    if ! command -v jq &> /dev/null; then
        missing_tools+=("jq")
    fi
    
    if [ ${#missing_tools[@]} -ne 0 ]; then
        log_error "Missing required tools: ${missing_tools[*]}"
        log_info "Please install the missing tools and try again."
        exit 1
    fi
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        log_error "AWS credentials not configured or invalid"
        log_info "Please run 'aws configure' to set up your credentials"
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

validate_environment() {
    local env="$1"
    
    case "$env" in
        dev|staging|prod)
            log_success "Environment '$env' is valid"
            ;;
        *)
            log_error "Invalid environment: $env"
            log_info "Valid environments: dev, staging, prod"
            exit 1
            ;;
    esac
}

setup_terraform_backend() {
    local env="$1"
    local region="$2"
    
    log_info "Setting up Terraform backend for $env environment..."
    
    local bucket_name="nautilus-arbitrage-terraform-state-${env}-${region}"
    local key="terraform.tfstate"
    
    # Create S3 bucket for Terraform state if it doesn't exist
    if ! aws s3 ls "s3://$bucket_name" 2>/dev/null; then
        log_info "Creating S3 bucket for Terraform state: $bucket_name"
        aws s3 mb "s3://$bucket_name" --region "$region"
        aws s3api put-bucket-versioning --bucket "$bucket_name" --versioning-configuration Status=Enabled
        aws s3api put-bucket-encryption --bucket "$bucket_name" --server-side-encryption-configuration '{
            "Rules": [{
                "ApplyServerSideEncryptionByDefault": {
                    "SSEAlgorithm": "AES256"
                }
            }]
        }'
    fi
    
    # Create backend configuration
    cat > "$TERRAFORM_DIR/backend.tf" << EOF
terraform {
  backend "s3" {
    bucket = "$bucket_name"
    key    = "$key"
    region = "$region"
  }
}
EOF
    
    log_success "Terraform backend configured"
}

deploy_terraform() {
    local env="$1"
    local region="$2"
    
    if [ "$SKIP_TERRAFORM" = true ]; then
        log_warning "Skipping Terraform deployment"
        return 0
    fi
    
    log_info "Deploying Terraform infrastructure for $env environment..."
    
    cd "$TERRAFORM_DIR"
    
    # Initialize Terraform
    terraform init
    
    # Create workspace if it doesn't exist
    terraform workspace select "$env" 2>/dev/null || terraform workspace new "$env"
    
    # Plan deployment
    log_info "Planning Terraform deployment..."
    terraform plan -var="environment=$env" -var="aws_region=$region" -out="terraform.tfplan"
    
    if [ "$DRY_RUN" = true ]; then
        log_info "Dry run mode - showing planned changes:"
        terraform show terraform.tfplan
        return 0
    fi
    
    # Apply deployment
    log_info "Applying Terraform deployment..."
    if [ "$AUTO_APPROVE" = true ]; then
        terraform apply terraform.tfplan
    else
        terraform apply terraform.tfplan
    fi
    
    log_success "Terraform deployment completed"
}

build_docker_image() {
    local env="$1"
    
    if [ "$SKIP_BUILD" = true ]; then
        log_warning "Skipping Docker image build"
        return 0
    fi
    
    log_info "Building Docker image for $env environment..."
    
    cd "$PROJECT_ROOT"
    
    # Build the image
    docker build -f "$DOCKER_DIR/Dockerfile" -t "nautilus-arbitrage:$env" .
    
    # Tag for ECR (if deploying to AWS)
    if [ "$SKIP_DOCKER" = false ]; then
        local account_id=$(aws sts get-caller-identity --query Account --output text)
        local region=$(aws configure get region)
        local ecr_uri="$account_id.dkr.ecr.$region.amazonaws.com/nautilus-arbitrage:$env"
        
        docker tag "nautilus-arbitrage:$env" "$ecr_uri"
        log_success "Docker image built and tagged for ECR: $ecr_uri"
    fi
    
    log_success "Docker image build completed"
}

deploy_docker() {
    local env="$1"
    
    if [ "$SKIP_DOCKER" = true ]; then
        log_warning "Skipping Docker deployment"
        return 0
    fi
    
    log_info "Deploying Docker containers for $env environment..."
    
    # Get ECR login token
    local account_id=$(aws sts get-caller-identity --query Account --output text)
    local region=$(aws configure get region)
    
    aws ecr get-login-password --region "$region" | docker login --username AWS --password-stdin "$account_id.dkr.ecr.$region.amazonaws.com"
    
    # Push image to ECR
    local ecr_uri="$account_id.dkr.ecr.$region.amazonaws.com/nautilus-arbitrage:$env"
    docker push "$ecr_uri"
    
    # Update ECS service
    local cluster_name="nautilus-arbitrage-$env-cluster"
    local service_name="nautilus-arbitrage-$env-service"
    
    log_info "Updating ECS service: $service_name"
    aws ecs update-service \
        --cluster "$cluster_name" \
        --service "$service_name" \
        --force-new-deployment
    
    log_success "Docker deployment completed"
}

show_deployment_info() {
    local env="$1"
    local region="$2"
    
    log_info "Deployment completed successfully!"
    echo
    echo "Environment: $env"
    echo "Region: $region"
    echo
    echo "Useful commands:"
    echo "  View logs: aws logs tail /ecs/nautilus-arbitrage-$env --follow"
    echo "  Check service: aws ecs describe-services --cluster nautilus-arbitrage-$env-cluster --services nautilus-arbitrage-$env-service"
    echo "  View dashboard: https://$region.console.aws.amazon.com/cloudwatch/home?region=$region#dashboards:name=nautilus-arbitrage-$env-dashboard"
    echo
}

# Parse command line arguments
AUTO_APPROVE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -r|--region)
            AWS_REGION="$2"
            shift 2
            ;;
        --skip-build)
            SKIP_BUILD=true
            shift
            ;;
        --skip-terraform)
            SKIP_TERRAFORM=true
            shift
            ;;
        --skip-docker)
            SKIP_DOCKER=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --auto-approve)
            AUTO_APPROVE=true
            shift
            ;;
        dev|staging|prod)
            ENVIRONMENT="$1"
            shift
            ;;
        *)
            log_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Validate environment
if [ -z "$ENVIRONMENT" ]; then
    log_error "Environment is required"
    show_help
    exit 1
fi

validate_environment "$ENVIRONMENT"

# Main deployment flow
log_info "Starting deployment for $ENVIRONMENT environment in $AWS_REGION region"

check_prerequisites
setup_terraform_backend "$ENVIRONMENT" "$AWS_REGION"
deploy_terraform "$ENVIRONMENT" "$AWS_REGION"
build_docker_image "$ENVIRONMENT"
deploy_docker "$ENVIRONMENT"
show_deployment_info "$ENVIRONMENT" "$AWS_REGION"

log_success "Deployment completed successfully!"
