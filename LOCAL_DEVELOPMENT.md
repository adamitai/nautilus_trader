# Local Development Setup

This guide helps you run the Nautilus Arbitrage Tools locally with Docker while connecting to your AWS PostgreSQL database.

## Quick Start

1. **Set up your environment file:**
   ```bash
   cp env.local.example .env
   # Edit .env with your actual credentials
   ```

2. **Run the application:**
   ```bash
   ./run-local.sh
   ```

## Configuration

### Database Configuration

You have two options:

#### Option 1: Use AWS RDS (Recommended)
- Edit `.env` file with your AWS RDS credentials
- Get your RDS endpoint from AWS Console or Terraform output
- The application will connect directly to your AWS database

#### Option 2: Use Local PostgreSQL (For Testing)
- Run with local database: `./run-local.sh --local-db`
- This creates a local PostgreSQL container for testing
- Data is stored in a Docker volume

### API Keys

You need to get API keys from your exchanges:

1. **Binance:**
   - Go to [Binance API Management](https://www.binance.com/en/my/settings/api-management)
   - Create a new API key
   - Add to `.env` file

2. **Coinbase:**
   - Go to [Coinbase API Settings](https://pro.coinbase.com/profile/api)
   - Create a new API key
   - Add to `.env` file

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DB_HOST` | Database host | `your-rds-endpoint.region.rds.amazonaws.com` |
| `DB_PORT` | Database port | `5432` |
| `DB_NAME` | Database name | `nautilus_arbitrage` |
| `DB_USER` | Database user | `postgres` |
| `DB_PASSWORD` | Database password | `your-password` |
| `BINANCE_API_KEY` | Binance API key | `your-binance-key` |
| `BINANCE_SECRET_KEY` | Binance secret | `your-binance-secret` |
| `COINBASE_API_KEY` | Coinbase API key | `your-coinbase-key` |
| `COINBASE_SECRET_KEY` | Coinbase secret | `your-coinbase-secret` |

## Getting Your AWS RDS Endpoint

If you deployed with Terraform, you can get the RDS endpoint with:

```bash
cd aws-infrastructure/terraform
terraform output rds_endpoint
```

Or check the AWS Console:
1. Go to RDS service
2. Find your database instance
3. Copy the endpoint from the "Connectivity & security" tab

## Running the Application

### With AWS RDS
```bash
./run-local.sh
```

### With Local PostgreSQL
```bash
./run-local.sh --local-db
```

### Manual Docker Commands
```bash
# Build and run with AWS RDS
docker-compose -f docker-compose.local.yml up --build

# Build and run with local PostgreSQL
docker-compose -f docker-compose.local.yml --profile local-db up --build
```

## Monitoring

- **Health Check:** http://localhost:8000/health
- **Logs:** Check the `logs/` directory
- **Data:** Check the `data/` directory
- **CSV Output:** Check the `csv_output/` directory

## Troubleshooting

### Database Connection Issues
- Verify your RDS endpoint is correct
- Check security groups allow connections from your IP
- Ensure the database is running and accessible

### API Key Issues
- Verify API keys are correct and active
- Check if API keys have the required permissions
- Some exchanges require IP whitelisting

### Docker Issues
- Make sure Docker Desktop is running
- Try rebuilding the image: `docker-compose -f docker-compose.local.yml build --no-cache`

## Development

The local setup mounts your source code directories, so changes to:
- `arbitrage_tools/` - Will be reflected immediately
- `strategies/` - Will be reflected immediately

You can restart the container to pick up changes:
```bash
docker-compose -f docker-compose.local.yml restart arbitrage-tools
```
