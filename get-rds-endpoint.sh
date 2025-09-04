#!/bin/bash

# Script to help get RDS endpoint
echo "🔍 Finding your RDS endpoint..."

# Try different methods to get the RDS endpoint
echo ""
echo "Method 1: Checking AWS CLI..."
if command -v aws &> /dev/null; then
    echo "Trying to get RDS instances..."
    aws rds describe-db-instances --region us-west-2 --query 'DBInstances[?contains(DBInstanceIdentifier, `nautilus`)].{Identifier:DBInstanceIdentifier,Endpoint:Endpoint.Address,Port:Endpoint.Port}' --output table 2>/dev/null || echo "❌ AWS CLI access denied"
else
    echo "❌ AWS CLI not found"
fi

echo ""
echo "Method 2: Checking Terraform state..."
if [ -f "aws-infrastructure/terraform/.terraform/terraform.tfstate" ]; then
    echo "Checking local Terraform state..."
    grep -i "rds\|endpoint" aws-infrastructure/terraform/.terraform/terraform.tfstate | head -5 || echo "❌ No RDS info in local state"
else
    echo "❌ No local Terraform state found"
fi

echo ""
echo "Method 3: Manual lookup required"
echo "📋 Please get your RDS endpoint manually:"
echo "   1. Go to AWS RDS Console: https://us-west-2.console.aws.amazon.com/rds/home?region=us-west-2"
echo "   2. Look for database with name containing 'nautilus' or 'arbitrage'"
echo "   3. Copy the 'Endpoint' value from 'Connectivity & security' tab"
echo "   4. Update your .env file with the endpoint"

echo ""
echo "Current .env file location: $(pwd)/.env"
echo "Edit it with: nano .env  or  code .env"
