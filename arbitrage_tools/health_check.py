#!/usr/bin/env python3
"""
Health check endpoint for Nautilus Trader Arbitrage Tools
This provides a simple HTTP server for Docker health checks
"""

import os
import sys
import json
import time
import signal
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HealthCheckHandler(BaseHTTPRequestHandler):
    """HTTP handler for health check endpoints"""
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/health':
            self.handle_health_check()
        elif self.path == '/status':
            self.handle_status()
        else:
            self.send_error(404, "Not Found")
    
    def handle_health_check(self):
        """Handle /health endpoint"""
        try:
            # Basic health check - can be extended with more checks
            health_status = {
                "status": "healthy",
                "timestamp": time.time(),
                "environment": os.getenv("ENVIRONMENT", "unknown"),
                "version": "1.0.0"
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(health_status).encode())
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            self.send_error(500, f"Health check failed: {str(e)}")
    
    def handle_status(self):
        """Handle /status endpoint with more detailed information"""
        try:
            status = {
                "status": "running",
                "timestamp": time.time(),
                "environment": os.getenv("ENVIRONMENT", "unknown"),
                "log_level": os.getenv("LOG_LEVEL", "INFO"),
                "data_dir": os.getenv("DATA_DIR", "/app/data"),
                "logs_dir": os.getenv("LOGS_DIR", "/app/logs"),
                "csv_output_dir": os.getenv("CSV_OUTPUT_DIR", "/app/csv_output"),
                "database_host": os.getenv("DB_HOST", "unknown"),
                "redis_url": os.getenv("REDIS_URL", "unknown"),
                "version": "1.0.0"
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(status, indent=2).encode())
            
        except Exception as e:
            logger.error(f"Status check failed: {e}")
            self.send_error(500, f"Status check failed: {str(e)}")
    
    def log_message(self, format, *args):
        """Override to reduce log noise"""
        pass

class HealthCheckServer:
    """Simple HTTP server for health checks"""
    
    def __init__(self, host='0.0.0.0', port=8000):
        self.host = host
        self.port = port
        self.server = None
        self.server_thread = None
        self.running = False
    
    def start(self):
        """Start the health check server"""
        try:
            self.server = HTTPServer((self.host, self.port), HealthCheckHandler)
            self.server_thread = Thread(target=self.server.serve_forever, daemon=True)
            self.server_thread.start()
            self.running = True
            logger.info(f"Health check server started on {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"Failed to start health check server: {e}")
            return False
    
    def stop(self):
        """Stop the health check server"""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            self.running = False
            logger.info("Health check server stopped")
    
    def is_running(self):
        """Check if server is running"""
        return self.running

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"Received signal {signum}, shutting down...")
    sys.exit(0)

def main():
    """Main function to run the health check server"""
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Get configuration from environment
    host = os.getenv('HEALTH_CHECK_HOST', '0.0.0.0')
    port = int(os.getenv('HEALTH_CHECK_PORT', '8000'))
    
    # Create and start health check server
    health_server = HealthCheckServer(host, port)
    
    if not health_server.start():
        logger.error("Failed to start health check server")
        sys.exit(1)
    
    try:
        # Keep the main thread alive
        while health_server.is_running():
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
    finally:
        health_server.stop()

if __name__ == "__main__":
    main()
