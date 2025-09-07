# Local Docker Deployment Guide

This guide will help you deploy the Nautilus Trader Arbitrage Tools locally using Docker before deploying to AWS.

## Prerequisites

- Docker and Docker Compose installed
- Git (to clone the repository)
- Basic understanding of Docker concepts

## Quick Start

1. **Clone and navigate to the repository:**
   ```bash
   git clone <repository-url>
   cd nautilus_trader
   ```

2. **Set up environment variables:**
   ```bash
   cp docker.env.example .env
   # Edit .env with your actual API keys
   ```

3. **Start the services:**
   ```bash
   # Start core services (app, postgres, redis)
   ./scripts/docker-local.sh start
   
   # Or start with monitoring (grafana, prometheus)
   ./scripts/docker-local.sh start-monitoring
   ```

4. **Check service status:**
   ```bash
   ./scripts/docker-local.sh status
   ```

5. **View logs:**
   ```bash
   ./scripts/docker-local.sh logs
   ```

## Services Overview

### Core Services

- **arbitrage-monitor**: Main application container
- **postgres**: PostgreSQL database
- **redis**: Redis cache

### Optional Services (with monitoring profile)

- **grafana**: Monitoring dashboard (http://localhost:3000)
- **prometheus**: Metrics collection (http://localhost:9090)

## Configuration

### Environment Variables

Create a `.env` file from the template:

```bash
cp docker.env.example .env
```

Key variables to configure:

```env
# Database Configuration
DB_HOST=postgres
DB_PORT=5432
DB_NAME=nautilus_arbitrage
DB_USER=nautilus
DB_PASSWORD=password

# API Keys (get these from your exchange accounts)
BINANCE_API_KEY=your_binance_api_key_here
BINANCE_API_SECRET=your_binance_api_secret_here
BYBIT_API_KEY=your_bybit_api_key_here
BYBIT_API_SECRET=your_bybit_api_secret_here
OKX_API_KEY=your_okx_api_key_here
OKX_API_SECRET=your_okx_api_secret_here
OKX_PASSPHRASE=your_okx_passphrase_here

# Application Configuration
ENVIRONMENT=local
LOG_LEVEL=DEBUG
```

### Ports

- **8000**: Application health check endpoint
- **5432**: PostgreSQL database
- **6379**: Redis cache
- **3000**: Grafana (with monitoring profile)
- **9090**: Prometheus (with monitoring profile)

## Usage

### Starting Services

```bash
# Start core services only
./scripts/docker-local.sh start

# Start with monitoring
./scripts/docker-local.sh start-monitoring
```

### Managing Services

```bash
# Check status
./scripts/docker-local.sh status

# View logs
./scripts/docker-local.sh logs [service-name]

# Stop services
./scripts/docker-local.sh stop

# Restart services
./scripts/docker-local.sh restart

# Clean up (removes volumes)
./scripts/docker-local.sh cleanup
```

### Manual Docker Compose Commands

If you prefer to use Docker Compose directly:

```bash
# Start core services
docker-compose -f docker-compose.local.yml up -d

# Start with monitoring
docker-compose -f docker-compose.local.yml --profile monitoring up -d

# View logs
docker-compose -f docker-compose.local.yml logs -f

# Stop services
docker-compose -f docker-compose.local.yml down
```

## Health Checks

The application includes health check endpoints:

- **GET /health**: Basic health status
- **GET /status**: Detailed status information

Test the health check:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/status
```

## Data Persistence

Data is persisted in Docker volumes:

- **postgres_data**: Database data
- **redis_data**: Redis cache data
- **grafana_data**: Grafana configuration (with monitoring)
- **prometheus_data**: Prometheus metrics (with monitoring)

Local directories are mounted for development:

- `./data` → `/app/data`
- `./logs` → `/app/logs`
- `./arbitrage_tools/csv_output` → `/app/csv_output`

## Development

### Code Changes

The arbitrage tools are mounted as volumes, so code changes are reflected immediately:

- `./arbitrage_tools` → `/app/arbitrage_tools`
- `./strategies` → `/app/strategies`

### Debugging

1. **View application logs:**
   ```bash
   ./scripts/docker-local.sh logs arbitrage-monitor
   ```

2. **Access database:**
   ```bash
   docker exec -it nautilus-postgres-local psql -U nautilus -d nautilus_arbitrage
   ```

3. **Access Redis:**
   ```bash
   docker exec -it nautilus-redis-local redis-cli
   ```

4. **Access application container:**
   ```bash
   docker exec -it nautilus-arbitrage-local bash
   ```

## Monitoring (Optional)

When using the monitoring profile, you can access:

- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090

### Setting up Grafana

1. Access Grafana at http://localhost:3000
2. Login with admin/admin
3. Add Prometheus as a data source:
   - URL: http://prometheus:9090
   - Access: Server (default)

## Troubleshooting

### Common Issues

1. **Port conflicts:**
   - Check if ports 8000, 5432, 6379 are already in use
   - Modify ports in docker-compose.local.yml if needed

2. **Permission issues:**
   - Ensure Docker has proper permissions
   - Check file permissions on mounted volumes

3. **API key errors:**
   - Verify API keys in .env file
   - Check if keys have proper permissions

4. **Database connection issues:**
   - Ensure PostgreSQL container is running
   - Check database credentials in .env

### Logs and Debugging

```bash
# View all logs
docker-compose -f docker-compose.local.yml logs

# View specific service logs
docker-compose -f docker-compose.local.yml logs arbitrage-monitor

# Follow logs in real-time
docker-compose -f docker-compose.local.yml logs -f
```

### Clean Restart

If you encounter issues, try a clean restart:

```bash
# Stop and remove everything
./scripts/docker-local.sh cleanup

# Start fresh
./scripts/docker-local.sh start
```

## Next Steps

Once you have the local Docker deployment working:

1. Test your arbitrage strategies
2. Verify all functionality works as expected
3. Configure monitoring and alerting
4. Prepare for AWS deployment using the AWS infrastructure

## Support

For issues with local deployment:

1. Check the logs: `./scripts/docker-local.sh logs`
2. Verify environment configuration
3. Ensure all prerequisites are met
4. Check Docker and Docker Compose versions

For more information, see the main project documentation.
