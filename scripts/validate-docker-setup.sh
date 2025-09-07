#!/bin/bash

# Docker Setup Validation Script
# This script validates the Docker setup without actually running containers

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

# Function to check if Docker is installed
check_docker_installed() {
    if command -v docker &> /dev/null; then
        print_success "Docker is installed: $(docker --version)"
        return 0
    else
        print_error "Docker is not installed"
        return 1
    fi
}

# Function to check if Docker Compose is installed
check_docker_compose_installed() {
    if command -v docker-compose &> /dev/null; then
        print_success "Docker Compose is installed: $(docker-compose --version)"
        return 0
    elif docker compose version &> /dev/null; then
        print_success "Docker Compose (plugin) is available: $(docker compose version)"
        return 0
    else
        print_error "Docker Compose is not installed"
        return 1
    fi
}

# Function to check if Docker is running
check_docker_running() {
    if docker info > /dev/null 2>&1; then
        print_success "Docker is running"
        return 0
    else
        print_error "Docker is not running"
        return 1
    fi
}

# Function to check required files
check_required_files() {
    local files=(
        "docker-compose.local.yml"
        "aws-infrastructure/docker/Dockerfile"
        "aws-infrastructure/docker/requirements.txt"
        "arbitrage_tools/health_check.py"
        "scripts/docker-local.sh"
    )
    
    print_status "Checking required files..."
    
    for file in "${files[@]}"; do
        if [ -f "$file" ]; then
            print_success "✓ $file exists"
        else
            print_error "✗ $file is missing"
            return 1
        fi
    done
    
    return 0
}

# Function to check environment file
check_env_file() {
    if [ -f ".env" ]; then
        print_success ".env file exists"
        
        # Check for required variables
        local required_vars=(
            "DB_HOST"
            "DB_PORT"
            "DB_NAME"
            "DB_USER"
            "DB_PASSWORD"
            "BINANCE_API_KEY"
            "BINANCE_API_SECRET"
        )
        
        print_status "Checking environment variables..."
        local missing_vars=()
        
        for var in "${required_vars[@]}"; do
            if grep -q "^${var}=" .env && ! grep -q "^${var}=your_.*_here" .env; then
                print_success "✓ $var is configured"
            else
                missing_vars+=("$var")
            fi
        done
        
        if [ ${#missing_vars[@]} -gt 0 ]; then
            print_warning "The following variables need to be configured:"
            for var in "${missing_vars[@]}"; do
                echo "  - $var"
            done
        fi
        
    else
        print_warning ".env file not found. Run: cp docker.env.example .env"
        return 1
    fi
}

# Function to check Docker Compose syntax
check_docker_compose_syntax() {
    print_status "Validating Docker Compose syntax..."
    
    if command -v docker-compose &> /dev/null; then
        if docker-compose -f docker-compose.local.yml config > /dev/null 2>&1; then
            print_success "Docker Compose syntax is valid"
            return 0
        else
            print_error "Docker Compose syntax is invalid"
            return 1
        fi
    elif docker compose version &> /dev/null; then
        if docker compose -f docker-compose.local.yml config > /dev/null 2>&1; then
            print_success "Docker Compose syntax is valid"
            return 0
        else
            print_error "Docker Compose syntax is invalid"
            return 1
        fi
    else
        print_warning "Cannot validate Docker Compose syntax (Docker Compose not available)"
        return 0
    fi
}

# Function to check directory structure
check_directory_structure() {
    print_status "Checking directory structure..."
    
    local dirs=(
        "data"
        "logs"
        "arbitrage_tools/csv_output"
    )
    
    for dir in "${dirs[@]}"; do
        if [ -d "$dir" ]; then
            print_success "✓ $dir exists"
        else
            print_warning "Directory $dir will be created automatically"
        fi
    done
}

# Function to show installation instructions
show_installation_instructions() {
    echo ""
    print_status "Docker Installation Instructions:"
    echo ""
    echo "For macOS:"
    echo "1. Install Docker Desktop: https://www.docker.com/products/docker-desktop/"
    echo "2. Or install via Homebrew: brew install --cask docker"
    echo "3. Start Docker Desktop application"
    echo ""
    echo "For Linux (Ubuntu/Debian):"
    echo "1. sudo apt-get update"
    echo "2. sudo apt-get install docker.io docker-compose"
    echo "3. sudo systemctl start docker"
    echo "4. sudo usermod -aG docker \$USER"
    echo "5. Log out and log back in"
    echo ""
    echo "For Windows:"
    echo "1. Install Docker Desktop: https://www.docker.com/products/docker-desktop/"
    echo "2. Start Docker Desktop application"
    echo ""
}

# Main validation function
main() {
    echo "Nautilus Trader Docker Setup Validation"
    echo "======================================"
    echo ""
    
    local errors=0
    
    # Check Docker installation
    if ! check_docker_installed; then
        errors=$((errors + 1))
        show_installation_instructions
    fi
    
    # Check Docker Compose installation
    if ! check_docker_compose_installed; then
        errors=$((errors + 1))
    fi
    
    # Check if Docker is running (only if installed)
    if command -v docker &> /dev/null; then
        if ! check_docker_running; then
            errors=$((errors + 1))
            print_warning "Start Docker Desktop or run: sudo systemctl start docker"
        fi
    fi
    
    # Check required files
    if ! check_required_files; then
        errors=$((errors + 1))
    fi
    
    # Check environment file
    if ! check_env_file; then
        errors=$((errors + 1))
    fi
    
    # Check Docker Compose syntax
    if ! check_docker_compose_syntax; then
        errors=$((errors + 1))
    fi
    
    # Check directory structure
    check_directory_structure
    
    echo ""
    echo "======================================"
    
    if [ $errors -eq 0 ]; then
        print_success "All checks passed! You can now run:"
        echo "  ./scripts/docker-local.sh start"
        echo ""
        print_status "Next steps:"
        echo "1. Configure your API keys in .env file"
        echo "2. Run: ./scripts/docker-local.sh start"
        echo "3. Check status: ./scripts/docker-local.sh status"
        echo "4. View logs: ./scripts/docker-local.sh logs"
    else
        print_error "Found $errors issue(s) that need to be resolved"
        echo ""
        print_status "Common solutions:"
        echo "1. Install Docker and Docker Compose"
        echo "2. Start Docker service"
        echo "3. Configure .env file with your API keys"
        echo "4. Check file permissions"
    fi
    
    exit $errors
}

# Run main function
main "$@"
