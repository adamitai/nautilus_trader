#!/bin/bash

# Nautilus Trader Local Docker Deployment Script
# This script helps you deploy the arbitrage tools locally using Docker

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

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    print_success "Docker is running"
}

# Function to check if .env file exists
check_env_file() {
    if [ ! -f ".env" ]; then
        print_warning ".env file not found. Creating from template..."
        if [ -f "docker.env.example" ]; then
            cp docker.env.example .env
            print_success "Created .env file from docker.env.example"
            print_warning "Please edit .env file with your actual API keys before running the application"
        else
            print_error "docker.env.example file not found. Please create a .env file manually."
            exit 1
        fi
    else
        print_success ".env file found"
    fi
}

# Function to create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    mkdir -p data logs arbitrage_tools/csv_output
    print_success "Directories created"
}

# Function to build and start services
start_services() {
    local profile=""
    if [ "$1" = "monitoring" ]; then
        profile="--profile monitoring"
        print_status "Starting services with monitoring..."
    else
        print_status "Starting core services..."
    fi
    
    docker compose -f docker-compose.local.yml up --build -d $profile
    print_success "Services started"
}

# Function to show logs
show_logs() {
    local service=${1:-"arbitrage-monitor"}
    print_status "Showing logs for $service..."
    docker compose -f docker-compose.local.yml logs -f $service
}

# Function to stop services
stop_services() {
    print_status "Stopping services..."
    docker compose -f docker-compose.local.yml down
    print_success "Services stopped"
}

# Function to clean up
cleanup() {
    print_status "Cleaning up Docker resources..."
    docker compose -f docker-compose.local.yml down -v
    docker system prune -f
    print_success "Cleanup completed"
}

# Function to show status
show_status() {
    print_status "Service status:"
    docker compose -f docker-compose.local.yml ps
}

# Function to show help
show_help() {
    echo "Nautilus Trader Local Docker Deployment Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start           Start core services (app, postgres, redis)"
    echo "  start-monitoring Start all services including monitoring (grafana, prometheus)"
    echo "  stop            Stop all services"
    echo "  restart         Restart all services"
    echo "  logs [service]  Show logs (default: arbitrage-monitor)"
    echo "  status          Show service status"
    echo "  cleanup         Stop services and clean up Docker resources"
    echo "  help            Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start                    # Start core services"
    echo "  $0 start-monitoring         # Start with monitoring"
    echo "  $0 logs postgres           # Show postgres logs"
    echo "  $0 status                  # Show service status"
}

# Main script logic
case "${1:-help}" in
    start)
        check_docker
        check_env_file
        create_directories
        start_services
        print_success "Core services started successfully!"
        print_status "Access the application at: http://localhost:8000"
        print_status "PostgreSQL: localhost:5432"
        print_status "Redis: localhost:6379"
        ;;
    start-monitoring)
        check_docker
        check_env_file
        create_directories
        start_services monitoring
        print_success "All services started successfully!"
        print_status "Access the application at: http://localhost:8000"
        print_status "Grafana: http://localhost:3000 (admin/admin)"
        print_status "Prometheus: http://localhost:9090"
        print_status "PostgreSQL: localhost:5432"
        print_status "Redis: localhost:6379"
        ;;
    stop)
        stop_services
        ;;
    restart)
        stop_services
        sleep 2
        check_docker
        check_env_file
        create_directories
        start_services
        print_success "Services restarted successfully!"
        ;;
    logs)
        show_logs $2
        ;;
    status)
        show_status
        ;;
    cleanup)
        cleanup
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac
