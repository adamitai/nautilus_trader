#!/bin/bash

# Simple Update Script for Nautilus Trader Arbitrage
# Updates the running application with new code

set -euo pipefail

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }

# Configuration
AWS_REGION="us-east-1"
PROJECT_NAME="nautilus-arbitrage"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Build and push new image
update_image() {
    log_info "Building and pushing updated Docker image..."
    
    # Get ECR login token
    aws ecr get-login-password --region "$AWS_REGION" | docker login --username AWS --password-stdin "$(aws sts get-caller-identity --query Account --output text).dkr.ecr.$AWS_REGION.amazonaws.com"
    
    # Build frontend first
    log_info "Building React frontend..."
    "$PROJECT_ROOT/aws-infrastructure/scripts/build-frontend.sh"
    
    # Build new image (from project root)
    cd "$PROJECT_ROOT"
    docker build -f aws-infrastructure/docker/Dockerfile -t "$PROJECT_NAME:latest" .
    
    # Tag and push
    ECR_URI="$(aws sts get-caller-identity --query Account --output text).dkr.ecr.$AWS_REGION.amazonaws.com/$PROJECT_NAME:latest"
    docker tag "$PROJECT_NAME:latest" "$ECR_URI"
    docker push "$ECR_URI"
    
    log_success "New image pushed to ECR"
}

# Update ECS service
update_service() {
    log_info "Updating ECS service..."
    
    # Force new deployment
    aws ecs update-service \
        --cluster "$PROJECT_NAME-cluster" \
        --service "$PROJECT_NAME-service" \
        --force-new-deployment \
        --region "$AWS_REGION"
    
    log_success "ECS service updated"
    
    # Wait for deployment to complete
    log_info "Waiting for deployment to complete..."
    aws ecs wait services-stable \
        --cluster "$PROJECT_NAME-cluster" \
        --services "$PROJECT_NAME-service" \
        --region "$AWS_REGION"
    
    log_success "Deployment completed successfully!"
}

# Get updated URL
get_url() {
    log_info "Getting updated application URL..."
    
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
        
        log_success "Updated application is running at: http://$PUBLIC_IP:8000"
    else
        log_info "Check ECS console for service status"
    fi
}

# Main update function
main() {
    log_info "Starting application update..."
    
    update_image
    update_service
    get_url
    
    log_success "Update completed!"
}

# Run main function
main "$@"
