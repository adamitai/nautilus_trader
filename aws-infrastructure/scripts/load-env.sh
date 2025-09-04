#!/bin/bash

# Load environment variables from .env file
# This script loads the .env file and exports the variables

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

# Check if .env file exists
if [ ! -f "$ENV_FILE" ]; then
    log_error ".env file not found at $ENV_FILE"
    log_info "Please create a .env file based on env.example:"
    echo
    echo "  cp aws-infrastructure/env.example aws-infrastructure/.env"
    echo "  # Then edit aws-infrastructure/.env with your actual values"
    echo
    exit 1
fi

log_info "Loading environment variables from $ENV_FILE"

# Load environment variables
set -a  # automatically export all variables
source "$ENV_FILE"
set +a  # stop automatically exporting

# Validate required variables
required_vars=(
    "AWS_ACCESS_KEY_ID"
    "AWS_SECRET_ACCESS_KEY"
    "AWS_DEFAULT_REGION"
)

missing_vars=()
for var in "${required_vars[@]}"; do
    if [ -z "${!var:-}" ]; then
        missing_vars+=("$var")
    fi
done

if [ ${#missing_vars[@]} -ne 0 ]; then
    log_error "Missing required environment variables:"
    for var in "${missing_vars[@]}"; do
        echo "  - $var"
    done
    log_info "Please check your .env file and ensure all required variables are set"
    exit 1
fi

# Set AWS CLI environment variables
export AWS_ACCESS_KEY_ID
export AWS_SECRET_ACCESS_KEY
export AWS_DEFAULT_REGION

# Optional: Set session token if provided
if [ -n "${AWS_SESSION_TOKEN:-}" ]; then
    export AWS_SESSION_TOKEN
fi

log_success "Environment variables loaded successfully"
log_info "AWS Region: $AWS_DEFAULT_REGION"
log_info "Environment: ${ENVIRONMENT:-dev}"

# Verify AWS credentials
log_info "Verifying AWS credentials..."
if aws sts get-caller-identity >/dev/null 2>&1; then
    log_success "AWS credentials are valid"
    ACCOUNT_ID=$(aws sts get-caller-identity --query 'Account' --output text)
    log_info "AWS Account: $ACCOUNT_ID"
else
    log_error "AWS credentials are invalid or not configured properly"
    log_info "Please check your AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY in the .env file"
    exit 1
fi
