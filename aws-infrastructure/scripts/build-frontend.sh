#!/bin/bash

# Build Frontend Script for Nautilus Trader Arbitrage Tools
# This script builds the React frontend for production deployment

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FRONTEND_DIR="$PROJECT_ROOT/frontend"
DOCKER_DIR="$PROJECT_ROOT/docker"

log_info "Building React frontend for production..."

# Check if frontend directory exists
if [ ! -d "$FRONTEND_DIR" ]; then
    log_error "Frontend directory not found: $FRONTEND_DIR"
    exit 1
fi

# Check if package.json exists
if [ ! -f "$FRONTEND_DIR/package.json" ]; then
    log_error "package.json not found in frontend directory"
    exit 1
fi

# Navigate to frontend directory
cd "$FRONTEND_DIR"

# Check if node_modules exists, if not install dependencies
if [ ! -d "node_modules" ]; then
    log_info "Installing frontend dependencies..."
    npm install
fi

# Build the frontend
log_info "Building frontend for production..."
npm run build

# Check if build was successful
if [ ! -d "build" ]; then
    log_error "Frontend build failed - build directory not found"
    exit 1
fi

log_success "Frontend build completed successfully!"

# Copy build to docker directory
log_info "Copying build to docker directory..."
mkdir -p "$DOCKER_DIR/frontend"
cp -r build "$DOCKER_DIR/frontend/"

log_success "Frontend build copied to docker directory"
log_info "Ready for Docker image build!"
