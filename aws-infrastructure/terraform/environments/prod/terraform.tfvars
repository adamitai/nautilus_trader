# Production Environment Configuration

# General
project_name = "nautilus-arbitrage"
environment  = "prod"
aws_region   = "us-west-2"
owner        = "nautilus-team"

# Networking
vpc_cidr = "10.0.0.0/16"
enable_nat_gateway = true
enable_vpn_gateway = false

# Compute
container_image = "nautilus-arbitrage:prod"
container_cpu   = 2048
container_memory = 4096
min_capacity    = 2
max_capacity    = 10
enable_load_balancer = true

# Database
db_instance_class    = "db.r6g.large"
db_allocated_storage = 100
db_engine_version    = "15.4"

# Cache
cache_node_type = "cache.r6g.large"

# API Keys (set via environment variables or AWS Secrets Manager)
# These should be set securely, not in this file
binance_api_key    = ""
binance_api_secret = ""
bybit_api_key      = ""
bybit_api_secret   = ""
okx_api_key        = ""
okx_api_secret     = ""
okx_passphrase     = ""
