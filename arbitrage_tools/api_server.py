#!/usr/bin/env python3
"""
API Server for Nautilus Trader Arbitrage Tools
Provides REST endpoints for frontend communication with JWT authentication
"""

import os
import json
import time
import logging
import hashlib
import secrets
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
from typing import Dict, Any
import jwt
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Authentication configuration
JWT_SECRET = os.getenv('JWT_SECRET', secrets.token_urlsafe(32))
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24

# Default admin credentials (should be changed in production)
DEFAULT_ADMIN_USER = os.getenv('ADMIN_USER', 'admin')
DEFAULT_ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'nautilus2024!')

# Hash password for storage
def hash_password(password: str) -> str:
    """Hash password using SHA-256 with salt"""
    salt = secrets.token_hex(16)
    return f"{salt}:{hashlib.sha256((salt + password).encode()).hexdigest()}"

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    try:
        salt, hash_value = hashed.split(':')
        return hashlib.sha256((salt + password).encode()).hexdigest() == hash_value
    except:
        return False

def generate_token(user_id: str) -> str:
    """Generate JWT token"""
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_token(token: str) -> Dict[str, Any]:
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return {'error': 'Token expired'}
    except jwt.InvalidTokenError:
        return {'error': 'Invalid token'}

class ApiKeysManager:
    """Manages API keys storage and retrieval"""
    
    def __init__(self, keys_file: str = "api_keys.json"):
        self.keys_file = keys_file
        self.keys = self.load_keys()
    
    def load_keys(self) -> Dict[str, str]:
        """Load API keys from file"""
        try:
            if os.path.exists(self.keys_file):
                with open(self.keys_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load API keys: {e}")
        return {
            'binanceApiKey': '',
            'binanceApiSecret': '',
            'bybitApiKey': '',
            'bybitApiSecret': '',
            'okxApiKey': '',
            'okxApiSecret': '',
            'okxPassphrase': '',
        }
    
    def save_keys(self, keys: Dict[str, str]) -> bool:
        """Save API keys to file"""
        try:
            self.keys.update(keys)
            with open(self.keys_file, 'w') as f:
                json.dump(self.keys, f, indent=2)
            logger.info("API keys saved successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to save API keys: {e}")
            return False
    
    def get_keys(self) -> Dict[str, str]:
        """Get current API keys"""
        return self.keys.copy()
    
    def test_connection(self, exchange: str, keys: Dict[str, str]) -> bool:
        """Test API connection for a specific exchange"""
        try:
            if exchange == 'binance':
                return self._test_binance_connection(keys)
            elif exchange == 'bybit':
                return self._test_bybit_connection(keys)
            elif exchange == 'okx':
                return self._test_okx_connection(keys)
            else:
                return False
        except Exception as e:
            logger.error(f"Connection test failed for {exchange}: {e}")
            return False
    
    def _test_binance_connection(self, keys: Dict[str, str]) -> bool:
        """Test Binance API connection"""
        # Mock test - in real implementation, you would test actual API calls
        api_key = keys.get('binanceApiKey', '')
        api_secret = keys.get('binanceApiSecret', '')
        
        if not api_key or not api_secret:
            return False
        
        # Simulate API test
        time.sleep(1)  # Simulate network delay
        return len(api_key) > 10 and len(api_secret) > 10
    
    def _test_bybit_connection(self, keys: Dict[str, str]) -> bool:
        """Test Bybit API connection"""
        api_key = keys.get('bybitApiKey', '')
        api_secret = keys.get('bybitApiSecret', '')
        
        if not api_key or not api_secret:
            return False
        
        time.sleep(1)
        return len(api_key) > 10 and len(api_secret) > 10
    
    def _test_okx_connection(self, keys: Dict[str, str]) -> bool:
        """Test OKX API connection"""
        api_key = keys.get('okxApiKey', '')
        api_secret = keys.get('okxApiSecret', '')
        passphrase = keys.get('okxPassphrase', '')
        
        if not api_key or not api_secret or not passphrase:
            return False
        
        time.sleep(1)
        return len(api_key) > 10 and len(api_secret) > 10 and len(passphrase) > 5

class ApiRequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler for API endpoints"""
    
    def __init__(self, *args, keys_manager: ApiKeysManager = None, **kwargs):
        self.keys_manager = keys_manager
        super().__init__(*args, **kwargs)
    
    def require_auth(self):
        """Check if request is authenticated"""
        auth_header = self.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return False
        
        token = auth_header[7:]  # Remove 'Bearer ' prefix
        payload = verify_token(token)
        return 'error' not in payload
    
    def send_auth_error(self, message: str = "Authentication required"):
        """Send authentication error response"""
        self.send_response(401)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({"error": message}).encode())
    
    def send_json_response(self, data: Dict[str, Any], status_code: int = 200):
        """Send JSON response"""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def handle_login(self):
        """Handle /api/login endpoint"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            login_data = json.loads(post_data.decode('utf-8'))
            
            username = login_data.get('username', '')
            password = login_data.get('password', '')
            
            # Check credentials
            if username == DEFAULT_ADMIN_USER and password == DEFAULT_ADMIN_PASSWORD:
                token = generate_token(username)
                self.send_json_response({
                    "success": True,
                    "token": token,
                    "user": username,
                    "expires_in": JWT_EXPIRATION_HOURS * 3600
                })
            else:
                self.send_json_response({
                    "success": False,
                    "error": "Invalid credentials"
                }, 401)
                
        except Exception as e:
            logger.error(f"Login failed: {e}")
            self.send_json_response({
                "success": False,
                "error": "Login failed"
            }, 500)
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == '/health':
            self.handle_health_check()
        elif path == '/status':
            self.handle_status()
        elif path == '/api/keys':
            if not self.require_auth():
                self.send_auth_error()
                return
            self.handle_get_keys()
        else:
            self.send_error(404, "Not Found")
    
    def do_POST(self):
        """Handle POST requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == '/api/login':
            self.handle_login()
        elif path == '/api/keys':
            if not self.require_auth():
                self.send_auth_error()
                return
            self.handle_save_keys()
        elif path.startswith('/api/test-connection/'):
            if not self.require_auth():
                self.send_auth_error()
                return
            exchange = path.split('/')[-1]
            self.handle_test_connection(exchange)
        else:
            self.send_error(404, "Not Found")
    
    def handle_health_check(self):
        """Handle /health endpoint"""
        try:
            health_status = {
                "status": "healthy",
                "timestamp": time.time(),
                "environment": os.getenv("ENVIRONMENT", "local"),
                "version": "1.0.0"
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(health_status).encode())
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            self.send_error(500, f"Health check failed: {str(e)}")
    
    def handle_status(self):
        """Handle /status endpoint"""
        try:
            status = {
                "status": "running",
                "timestamp": time.time(),
                "environment": os.getenv("ENVIRONMENT", "local"),
                "log_level": os.getenv("LOG_LEVEL", "INFO"),
                "data_dir": os.getenv("DATA_DIR", "/app/data"),
                "logs_dir": os.getenv("LOGS_DIR", "/app/logs"),
                "csv_output_dir": os.getenv("CSV_OUTPUT_DIR", "/app/csv_output"),
                "database_host": os.getenv("DB_HOST", "postgres"),
                "redis_url": os.getenv("REDIS_URL", "redis://redis:6379/0"),
                "version": "1.0.0"
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(status, indent=2).encode())
            
        except Exception as e:
            logger.error(f"Status check failed: {e}")
            self.send_error(500, f"Status check failed: {str(e)}")
    
    def handle_get_keys(self):
        """Handle GET /api/keys endpoint"""
        try:
            keys = self.keys_manager.get_keys()
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(keys).encode())
            
        except Exception as e:
            logger.error(f"Failed to get API keys: {e}")
            self.send_error(500, f"Failed to get API keys: {str(e)}")
    
    def handle_save_keys(self):
        """Handle POST /api/keys endpoint"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            keys = json.loads(post_data.decode('utf-8'))
            
            success = self.keys_manager.save_keys(keys)
            
            if success:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"success": True, "message": "API keys saved successfully"}).encode())
            else:
                self.send_error(500, "Failed to save API keys")
                
        except Exception as e:
            logger.error(f"Failed to save API keys: {e}")
            self.send_error(500, f"Failed to save API keys: {str(e)}")
    
    def handle_test_connection(self, exchange: str):
        """Handle POST /api/test-connection/{exchange} endpoint"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            keys = json.loads(post_data.decode('utf-8'))
            
            success = self.keys_manager.test_connection(exchange, keys)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"success": success, "exchange": exchange}).encode())
            
        except Exception as e:
            logger.error(f"Failed to test connection for {exchange}: {e}")
            self.send_error(500, f"Failed to test connection: {str(e)}")
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def log_message(self, format, *args):
        """Override to reduce log noise"""
        pass

def create_handler(keys_manager):
    """Create a request handler with the keys manager"""
    def handler(*args, **kwargs):
        return ApiRequestHandler(*args, keys_manager=keys_manager, **kwargs)
    return handler

def main():
    """Main function to run the API server"""
    # Get configuration from environment
    host = os.getenv('API_HOST', '0.0.0.0')
    port = int(os.getenv('API_PORT', '8000'))
    
    # Create keys manager
    keys_manager = ApiKeysManager()
    
    # Create server
    handler = create_handler(keys_manager)
    server = HTTPServer((host, port), handler)
    
    logger.info(f"API Server starting on {host}:{port}")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("API Server shutting down...")
        server.shutdown()

if __name__ == "__main__":
    main()
