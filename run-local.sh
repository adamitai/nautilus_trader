#!/bin/bash

# Nautilus Arbitrage Tools - Local Development Setup
# This script helps you run the arbitrage tools locally with Docker

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if .env file exists
if [ ! -f ".env" ]; then
    print_warning ".env file not found!"
    print_status "Creating .env file from template..."
    cp env.local.example .env
    print_warning "Please edit .env file with your actual database credentials and API keys"
    print_status "You can get your RDS endpoint from AWS Console or Terraform output"
    exit 1
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker Desktop and try again."
    exit 1
fi

# Create necessary directories
print_status "Creating data directories..."
mkdir -p data logs csv_output

# Parse command line arguments
MODE="aws"  # Default to AWS RDS
while [[ $# -gt 0 ]]; do
    case $1 in
        --local-db)
            MODE="local"
            shift
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --local-db    Use local PostgreSQL instead of AWS RDS"
            echo "  --help        Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                    # Run with AWS RDS"
            echo "  $0 --local-db         # Run with local PostgreSQL"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Start the services
if [ "$MODE" = "local" ]; then
    print_status "Starting with local PostgreSQL database..."
    docker-compose -f docker-compose.local.yml --profile local-db up --build
else
    print_status "Starting with AWS RDS database..."
    print_warning "Make sure your .env file has the correct AWS RDS credentials"
    docker-compose -f docker-compose.local.yml up --build
fi
