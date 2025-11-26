#!/usr/bin/env python3
"""
uDOS Base Server - Shared Foundation for Web Extensions
Provides common server functionality, logging, health checks
"""

import http.server
import socketserver
import json
import os
import sys
import signal
import atexit
from pathlib import Path
from typing import Optional, Dict, Callable
import logging
from logging.handlers import RotatingFileHandler

from .port_manager import get_port_manager


class BaseExtensionHandler(http.server.SimpleHTTPRequestHandler):
    """Base handler with CORS, logging, and common functionality"""

    extension_name = "unknown"
    extension_root = None
    logger = None

    def end_headers(self):
        """Add CORS and cache control headers"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

    def do_OPTIONS(self):
        """Handle preflight requests"""
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        """Handle GET with logging"""
        if self.logger:
            self.logger.debug(f"GET {self.path} from {self.client_address[0]}")

        # Health check endpoint
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            health_data = json.dumps({
                'status': 'healthy',
                'extension': self.extension_name,
                'uptime': os.times().elapsed if hasattr(os.times(), 'elapsed') else 0
            })
            self.wfile.write(health_data.encode())
            return

        # Status endpoint
        if self.path == '/status':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            status_data = json.dumps({
                'extension': self.extension_name,
                'version': '1.0',
                'ready': True
            })
            self.wfile.write(status_data.encode())
            return

        super().do_GET()

    def log_message(self, format, *args):
        """Override to use our logger"""
        if self.logger:
            self.logger.info(format % args)
        else:
            super().log_message(format, *args)


class BaseExtensionServer:
    """Base server class for web extensions"""

    def __init__(self, name: str, port: int, root_dir: Path,
                 handler_class: Optional[type] = None,
                 api_url: str = 'http://localhost:5001/api'):
        self.name = name
        self.port = port
        self.root_dir = root_dir
        self.handler_class = handler_class or BaseExtensionHandler
        self.api_url = api_url
        self.port_manager = get_port_manager()
        self.httpd = None

        # Setup logging
        self.log_dir = Path(__file__).parent.parent.parent.parent / 'memory' / 'logs'
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.logger = self._setup_logging()

        # Configure handler class
        self.handler_class.extension_name = name
        self.handler_class.extension_root = root_dir
        self.handler_class.logger = self.logger

        # Register cleanup
        atexit.register(self.cleanup)
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)

    def _setup_logging(self) -> logging.Logger:
        """Setup rotating file logger"""
        logger = logging.getLogger(f'uDOS.{self.name}')
        logger.setLevel(logging.DEBUG)

        # File handler with rotation
        log_file = self.log_dir / f'{self.name.lower()}_server.log'
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)

        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        return logger

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"Received signal {signum}, shutting down...")
        self.cleanup()
        sys.exit(0)

    def start(self, auto_cleanup: bool = True) -> bool:
        """Start server with port management"""
        self.logger.info(f"Starting {self.name} server on port {self.port}...")

        # Cleanup port if requested
        if auto_cleanup:
            if not self.port_manager.cleanup_port(self.port):
                self.logger.error(f"Failed to cleanup port {self.port}")

                # Try to find alternative port
                alt_port = self.port_manager.find_available_port(self.port)
                if alt_port:
                    self.logger.warning(f"Using alternative port {alt_port}")
                    self.port = alt_port
                else:
                    return False

        # Start server
        try:
            # Change to extension directory
            os.chdir(self.root_dir)

            # Create server
            socketserver.TCPServer.allow_reuse_address = True
            self.httpd = socketserver.TCPServer(('127.0.0.1', self.port), self.handler_class)

            # Register with port manager
            self.port_manager.register_server(self.port, self.name)

            self.logger.info(f"✓ {self.name} server running on http://localhost:{self.port}")
            print(f"✓ {self.name} server running on http://localhost:{self.port}")

            # Serve forever
            self.httpd.serve_forever()

        except OSError as e:
            self.logger.error(f"Failed to start server: {e}")
            return False
        except KeyboardInterrupt:
            self.logger.info("Server stopped by user")
            return True
        except Exception as e:
            self.logger.error(f"Server error: {e}", exc_info=True)
            return False
        finally:
            self.cleanup()

        return True

    def cleanup(self):
        """Cleanup server resources"""
        if self.httpd:
            self.logger.info(f"Shutting down {self.name} server...")
            try:
                self.httpd.shutdown()
                self.httpd.server_close()
            except Exception as e:
                self.logger.error(f"Error during shutdown: {e}")

        # Unregister from port manager
        self.port_manager.unregister_server(self.port)
        self.logger.info(f"{self.name} server stopped")

    def is_healthy(self) -> bool:
        """Check server health"""
        return self.port_manager.health_check(self.port)
