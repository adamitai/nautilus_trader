#!/bin/bash

# Nautilus Trader Arbitrage Tools - AWS Setup Script
# This script sets up AWS CLI, Terraform, and other required tools

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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
Nautilus Trader Arbitrage Tools - AWS Setup Script

This script installs and configures the required tools for AWS deployment.

USAGE:
    $0 [OPTIONS]

OPTIONS:
    -h, --help              Show this help message
    --skip-aws-cli          Skip AWS CLI installation
    --skip-terraform        Skip Terraform installation
    --skip-docker           Skip Docker installation
    --configure-only        Only configure existing tools, don't install

EXAMPLES:
    $0                      # Install and configure all tools
    $0 --configure-only     # Only configure existing tools
    $0 --skip-docker        # Install everything except Docker

EOF
}

detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
    elif [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        OS="windows"
    else
        log_error "Unsupported operating system: $OSTYPE"
        exit 1
    fi
    
    log_info "Detected operating system: $OS"
}

install_aws_cli() {
    if command -v aws &> /dev/null; then
        log_info "AWS CLI is already installed: $(aws --version)"
        return 0
    fi
    
    log_info "Installing AWS CLI..."
    
    case $OS in
        linux)
            curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
            unzip awscliv2.zip
            sudo ./aws/install
            rm -rf aws awscliv2.zip
            ;;
        macos)
            if command -v brew &> /dev/null; then
                brew install awscli
            else
                curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
                sudo installer -pkg AWSCLIV2.pkg -target /
                rm AWSCLIV2.pkg
            fi
            ;;
        windows)
            log_error "Please install AWS CLI manually on Windows"
            log_info "Download from: https://awscli.amazonaws.com/AWSCLIV2.msi"
            exit 1
            ;;
    esac
    
    log_success "AWS CLI installed successfully"
}

install_terraform() {
    if command -v terraform &> /dev/null; then
        log_info "Terraform is already installed: $(terraform --version | head -n1)"
        return 0
    fi
    
    log_info "Installing Terraform..."
    
    case $OS in
        linux)
            wget -O- https://apt.releases.hashicorp.com/gpg | gpg --dearmor | sudo tee /usr/share/keyrings/hashicorp-archive-keyring.gpg
            echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
            sudo apt update && sudo apt install terraform
            ;;
        macos)
            if command -v brew &> /dev/null; then
                brew tap hashicorp/tap
                brew install hashicorp/tap/terraform
            else
                log_error "Homebrew not found. Please install Terraform manually."
                exit 1
            fi
            ;;
        windows)
            log_error "Please install Terraform manually on Windows"
            log_info "Download from: https://www.terraform.io/downloads"
            exit 1
            ;;
    esac
    
    log_success "Terraform installed successfully"
}

install_docker() {
    if command -v docker &> /dev/null; then
        log_info "Docker is already installed: $(docker --version)"
        return 0
    fi
    
    log_info "Installing Docker..."
    
    case $OS in
        linux)
            curl -fsSL https://get.docker.com -o get-docker.sh
            sudo sh get-docker.sh
            sudo usermod -aG docker $USER
            rm get-docker.sh
            log_warning "Please log out and back in for Docker group changes to take effect"
            ;;
        macos)
            log_info "Please install Docker Desktop for Mac manually"
            log_info "Download from: https://www.docker.com/products/docker-desktop"
            ;;
        windows)
            log_info "Please install Docker Desktop for Windows manually"
            log_info "Download from: https://www.docker.com/products/docker-desktop"
            ;;
    esac
    
    log_success "Docker installation instructions provided"
}

install_jq() {
    if command -v jq &> /dev/null; then
        log_info "jq is already installed: $(jq --version)"
        return 0
    fi
    
    log_info "Installing jq..."
    
    case $OS in
        linux)
            sudo apt update && sudo apt install jq
            ;;
        macos)
            if command -v brew &> /dev/null; then
                brew install jq
            else
                log_error "Homebrew not found. Please install jq manually."
                exit 1
            fi
            ;;
        windows)
            log_error "Please install jq manually on Windows"
            log_info "Download from: https://stedolan.github.io/jq/"
            exit 1
            ;;
    esac
    
    log_success "jq installed successfully"
}

configure_aws_cli() {
    log_info "Configuring AWS CLI..."
    
    if aws sts get-caller-identity &> /dev/null; then
        log_info "AWS CLI is already configured"
        aws sts get-caller-identity
        return 0
    fi
    
    log_warning "AWS CLI is not configured"
    log_info "Please run 'aws configure' to set up your credentials:"
    echo
    echo "  AWS Access Key ID: [Your access key]"
    echo "  AWS Secret Access Key: [Your secret key]"
    echo "  Default region name: us-west-2"
    echo "  Default output format: json"
    echo
    
    read -p "Would you like to configure AWS CLI now? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        aws configure
    else
        log_warning "Please configure AWS CLI manually before deploying"
    fi
}

create_ecr_repository() {
    log_info "Creating ECR repository..."
    
    local region=$(aws configure get region || echo "us-west-2")
    local account_id=$(aws sts get-caller-identity --query Account --output text 2>/dev/null || echo "")
    
    if [ -z "$account_id" ]; then
        log_warning "Cannot create ECR repository - AWS CLI not configured"
        return 0
    fi
    
    # Create ECR repository if it doesn't exist
    if ! aws ecr describe-repositories --repository-names nautilus-arbitrage --region "$region" &> /dev/null; then
        aws ecr create-repository --repository-name nautilus-arbitrage --region "$region"
        log_success "ECR repository created: $account_id.dkr.ecr.$region.amazonaws.com/nautilus-arbitrage"
    else
        log_info "ECR repository already exists"
    fi
}

show_next_steps() {
    log_success "Setup completed successfully!"
    echo
    echo "Next steps:"
    echo "1. Configure your API keys in AWS Secrets Manager or environment variables"
    echo "2. Run the deployment script:"
    echo "   ./aws-infrastructure/scripts/deploy.sh dev"
    echo
    echo "For more information, see:"
    echo "  - aws-infrastructure/docs/DEPLOYMENT.md"
    echo "  - aws-infrastructure/README.md"
    echo
}

# Parse command line arguments
SKIP_AWS_CLI=false
SKIP_TERRAFORM=false
SKIP_DOCKER=false
CONFIGURE_ONLY=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        --skip-aws-cli)
            SKIP_AWS_CLI=true
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
        --configure-only)
            CONFIGURE_ONLY=true
            shift
            ;;
        *)
            log_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Main setup flow
log_info "Starting AWS setup..."

detect_os

if [ "$CONFIGURE_ONLY" = false ]; then
    if [ "$SKIP_AWS_CLI" = false ]; then
        install_aws_cli
    fi
    
    if [ "$SKIP_TERRAFORM" = false ]; then
        install_terraform
    fi
    
    if [ "$SKIP_DOCKER" = false ]; then
        install_docker
    fi
    
    install_jq
fi

configure_aws_cli
create_ecr_repository
show_next_steps

log_success "AWS setup completed successfully!"
