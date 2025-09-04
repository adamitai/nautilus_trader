#!/bin/bash

# Setup script to create .env file and prepare for deployment

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

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
ENV_FILE="$PROJECT_ROOT/.env"
ENV_EXAMPLE="$PROJECT_ROOT/env.example"

log_info "Setting up environment for Nautilus Arbitrage deployment"

# Check if .env already exists
if [ -f "$ENV_FILE" ]; then
    log_warning ".env file already exists at $ENV_FILE"
    read -p "Do you want to overwrite it? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Keeping existing .env file"
        exit 0
    fi
fi

# Copy example file
if [ -f "$ENV_EXAMPLE" ]; then
    cp "$ENV_EXAMPLE" "$ENV_FILE"
    log_success "Created .env file from template"
else
    log_error "env.example file not found at $ENV_EXAMPLE"
    exit 1
fi

echo
log_info "Please edit the .env file with your actual values:"
echo "  nano aws-infrastructure/.env"
echo
log_info "Required values to configure:"
echo "  - AWS_ACCESS_KEY_ID: Your AWS access key"
echo "  - AWS_SECRET_ACCESS_KEY: Your AWS secret key"
echo "  - AWS_DEFAULT_REGION: Your preferred AWS region (e.g., us-west-2)"
echo "  - BINANCE_API_KEY: Your Binance API key"
echo "  - BINANCE_API_SECRET: Your Binance API secret"
echo "  - BYBIT_API_KEY: Your Bybit API key"
echo "  - BYBIT_API_SECRET: Your Bybit API secret"
echo "  - OKX_API_KEY: Your OKX API key"
echo "  - OKX_API_SECRET: Your OKX API secret"
echo "  - OKX_PASSPHRASE: Your OKX passphrase"
echo

read -p "Press Enter when you've configured the .env file..."

# Validate the .env file
if [ -f "$ENV_FILE" ]; then
    log_info "Validating .env file..."
    
    # Source the .env file
    set -a
    source "$ENV_FILE"
    set +a
    
    # Check required variables
    required_vars=(
        "AWS_ACCESS_KEY_ID"
        "AWS_SECRET_ACCESS_KEY"
        "AWS_DEFAULT_REGION"
    )
    
    missing_vars=()
    for var in "${required_vars[@]}"; do
        if [ -z "${!var:-}" ] || [ "${!var}" = "your_aws_access_key_here" ] || [ "${!var}" = "your_aws_secret_access_key_here" ]; then
            missing_vars+=("$var")
        fi
    done
    
    if [ ${#missing_vars[@]} -ne 0 ]; then
        log_error "Please configure the following variables in .env:"
        for var in "${missing_vars[@]}"; do
            echo "  - $var"
        done
        exit 1
    fi
    
    log_success ".env file validation passed"
    
    # Test AWS credentials
    log_info "Testing AWS credentials..."
    export AWS_ACCESS_KEY_ID
    export AWS_SECRET_ACCESS_KEY
    export AWS_DEFAULT_REGION
    
    if aws sts get-caller-identity >/dev/null 2>&1; then
        log_success "AWS credentials are valid"
        aws sts get-caller-identity --query 'Account' --output text | xargs -I {} log_info "AWS Account: {}"
    else
        log_error "AWS credentials are invalid"
        log_info "Please check your AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY"
        exit 1
    fi
else
    log_error ".env file not found"
    exit 1
fi

echo
log_success "Environment setup completed successfully!"
echo
log_info "Next steps:"
echo "1. Review your .env file: nano aws-infrastructure/.env"
echo "2. Deploy to development: ./aws-infrastructure/scripts/deploy.sh dev"
echo "3. Deploy to production: ./aws-infrastructure/scripts/deploy.sh prod"
echo
log_warning "Remember: Never commit your .env file to version control!"
