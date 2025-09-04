# AWS Credentials Setup Guide

## 🔑 **Where to Get Your AWS Credentials**

### **Step 1: Go to AWS Console**
1. Open your browser and go to: https://console.aws.amazon.com
2. Sign in with your AWS account

### **Step 2: Create IAM User (Recommended)**
1. **Search for "IAM"** in the AWS services search bar
2. **Click "Users"** in the left sidebar
3. **Click "Create user"**
4. **User name**: `nautilus-arbitrage-user`
5. **Select "Programmatic access"** (check the box)
6. **Click "Next: Permissions"**

### **Step 3: Attach Policies**
1. **Click "Attach existing policies directly"**
2. **Search for and select**: `AdministratorAccess`
   - This gives full access needed for deployment
   - For production, you might want more restrictive policies
3. **Click "Next: Tags"** (optional)
4. **Click "Next: Review"**
5. **Click "Create user"**

### **Step 4: Get Your Credentials**
1. **IMPORTANT**: You'll see a screen with your credentials
2. **Copy these values**:
   - **Access Key ID**: `AKIA...` (starts with AKIA)
   - **Secret Access Key**: `...` (long random string)
3. **Click "Download .csv"** to save them securely
4. **⚠️ WARNING**: You can only see the secret key once!

### **Step 5: Configure Your .env File**

Now edit your `.env` file:

```bash
# Open the .env file
nano aws-infrastructure/.env
```

Replace these values with your actual credentials:

```bash
# AWS Configuration
AWS_ACCESS_KEY_ID=AKIA...your_actual_access_key_here
AWS_SECRET_ACCESS_KEY=your_actual_secret_key_here
AWS_DEFAULT_REGION=us-west-2

# Exchange API Keys (you'll need these too)
BINANCE_API_KEY=your_binance_api_key_here
BINANCE_API_SECRET=your_binance_api_secret_here
BYBIT_API_KEY=your_bybit_api_key_here
BYBIT_API_SECRET=your_bybit_api_secret_here
OKX_API_KEY=your_okx_api_key_here
OKX_API_SECRET=your_okx_api_secret_here
OKX_PASSPHRASE=your_okx_passphrase_here
```

## 🔒 **Security Best Practices**

### **For Development:**
- Use `AdministratorAccess` policy for simplicity
- Keep credentials in `.env` file (never commit to git)

### **For Production:**
- Create custom IAM policies with minimal required permissions
- Use AWS Secrets Manager for API keys
- Enable MFA on your AWS account
- Rotate access keys regularly

## 🚀 **Quick Test**

After setting up your credentials, test them:

```bash
# Test AWS credentials
aws sts get-caller-identity

# Should return something like:
# {
#     "UserId": "AIDACKCEVSQ6C2EXAMPLE",
#     "Account": "123456789012",
#     "Arn": "arn:aws:iam::123456789012:user/nautilus-arbitrage-user"
# }
```

## 🆘 **Troubleshooting**

### **"Invalid credentials" error:**
- Double-check your Access Key ID and Secret Access Key
- Make sure there are no extra spaces or characters
- Verify the IAM user has the correct permissions

### **"Access denied" error:**
- Make sure you attached the `AdministratorAccess` policy
- Check if your AWS account has billing enabled

### **"Region not found" error:**
- Use a valid AWS region like `us-west-2`, `us-east-1`, `eu-west-1`

## 📞 **Need Help?**

1. **AWS Documentation**: https://docs.aws.amazon.com/IAM/
2. **AWS Support**: Available in AWS Console
3. **Check your .env file**: Make sure all values are correct

---

**Once you have your credentials, you can deploy with:**
```bash
./aws-infrastructure/scripts/deploy.sh dev
```

