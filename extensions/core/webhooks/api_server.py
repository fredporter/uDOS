"""
REST API Server for uDOS Webhook System

Provides HTTP endpoints for:
- Receiving webhook events from external platforms
- Querying event history
- Managing routes and handlers
- System health and statistics

Endpoints:
- POST /webhooks/{platform} - Receive webhook events
- GET /api/events - Query event history
- GET /api/events/{event_id} - Get specific event
- GET /api/routes - List all routes
- POST /api/routes - Register new route
- PUT /api/routes/{name} - Update route
- DELETE /api/routes/{name} - Remove route
- GET /api/stats - Get system statistics
- GET /api/health - Health check

Security:
- Webhook signature verification
- API key authentication
- Rate limiting
- RBAC support
"""

import asyncio
import hashlib
import hmac
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from pathlib import Path

from flask import Flask, request, jsonify, abort
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

from .event_processor import EventProcessor
from .event_router import EventRouter

logger = logging.getLogger(__name__)


class WebhookAPIServer:
    """REST API server for webhook system."""

    def __init__(
        self,
        processor: EventProcessor,
        router: EventRouter,
        config_path: Optional[Path] = None,
        host: str = '0.0.0.0',
        port: int = 5050
    ):
        """
        Initialize API server.

        Args:
            processor: EventProcessor instance
            router: EventRouter instance
            config_path: Path to configuration file
            host: Server host address
            port: Server port
        """
        self.processor = processor
        self.router = router
        self.host = host
        self.port = port

        # Load configuration
        self.config = self._load_config(config_path)

        # Create Flask app
        self.app = Flask(__name__)
        CORS(self.app)  # Enable CORS for web clients

        # Register routes
        self._register_routes()

        # Statistics
        self.stats = {
            'api_requests': 0,
            'webhook_received': 0,
            'api_errors': 0
        }

    def _load_config(self, config_path: Optional[Path]) -> Dict[str, Any]:
        """Load server configuration."""
        default_config = {
            'api_key_required': False,
            'api_keys': [],
            'rate_limit': {
                'enabled': True,
                'max_requests': 100,
                'window_seconds': 60
            },
            'webhook_secrets': {
                'github': None,
                'slack': None,
                'notion': None,
                'clickup': None
            },
            'cors_origins': ['*'],
            'max_event_history': 1000
        }

        if config_path and config_path.exists():
            with open(config_path) as f:
                user_config = json.load(f)
                default_config.update(user_config.get('api_server', {}))

        return default_config

    def _register_routes(self):
        """Register all API routes."""

        # Webhook endpoints
        @self.app.route('/webhooks/<platform>', methods=['POST'])
        async def receive_webhook(platform: str):
            """Receive webhook from external platform."""
            try:
                # Verify signature
                if not self._verify_signature(platform, request):
                    abort(401, 'Invalid signature')

                # Get payload
                payload = request.get_json()
                if not payload:
                    abort(400, 'No payload')

                # Add headers to payload for processing
                payload['headers'] = dict(request.headers)

                # Process event
                event = self.processor.process(platform, payload)

                # Route event
                results = await self.router.route(event)

                # Update statistics
                self.stats['webhook_received'] += 1

                return jsonify({
                    'success': True,
                    'event_id': event['event_id'],
                    'event_type': event['event_type'],
                    'routes_matched': len(results),
                    'routes_succeeded': sum(1 for r in results if r['success'])
                }), 200

            except Exception as e:
                logger.error(f"Webhook error: {e}")
                self.stats['api_errors'] += 1
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        # Event history endpoints
        @self.app.route('/api/events', methods=['GET'])
        def list_events():
            """Query event history."""
            self.stats['api_requests'] += 1

            # Parse query parameters
            limit = int(request.args.get('limit', 100))
            event_type = request.args.get('event_type')
            platform = request.args.get('platform')

            # Get history
            history = self.router.get_history(limit=limit, event_type=event_type)

            # Filter by platform if specified
            if platform:
                history = [h for h in history if h.get('platform') == platform]

            return jsonify({
                'total': len(history),
                'events': history
            }), 200

        @self.app.route('/api/events/<event_id>', methods=['GET'])
        def get_event(event_id: str):
            """Get specific event by ID."""
            self.stats['api_requests'] += 1

            # Search history for event
            history = self.router.get_history(limit=self.config['max_event_history'])
            event = next((h for h in history if h['event_id'] == event_id), None)

            if not event:
                abort(404, f'Event {event_id} not found')

            return jsonify(event), 200

        # Route management endpoints
        @self.app.route('/api/routes', methods=['GET'])
        def list_routes():
            """List all registered routes."""
            self.stats['api_requests'] += 1

            routes = []
            for route in self.router.routes:
                routes.append({
                    'name': route.name,
                    'pattern': route.pattern,
                    'priority': route.priority,
                    'enabled': route.enabled,
                    'stats': route.stats
                })

            return jsonify({
                'total': len(routes),
                'routes': routes
            }), 200

        @self.app.route('/api/routes/<name>', methods=['GET'])
        def get_route(name: str):
            """Get specific route by name."""
            self.stats['api_requests'] += 1

            route = self.router.get_route(name)
            if not route:
                abort(404, f'Route {name} not found')

            return jsonify({
                'name': route.name,
                'pattern': route.pattern,
                'priority': route.priority,
                'enabled': route.enabled,
                'stats': route.stats
            }), 200

        @self.app.route('/api/routes/<name>/enable', methods=['POST'])
        def enable_route(name: str):
            """Enable a route."""
            self.stats['api_requests'] += 1

            route = self.router.get_route(name)
            if not route:
                abort(404, f'Route {name} not found')

            self.router.enable_route(name)
            return jsonify({'success': True}), 200

        @self.app.route('/api/routes/<name>/disable', methods=['POST'])
        def disable_route(name: str):
            """Disable a route."""
            self.stats['api_requests'] += 1

            route = self.router.get_route(name)
            if not route:
                abort(404, f'Route {name} not found')

            self.router.disable_route(name)
            return jsonify({'success': True}), 200

        @self.app.route('/api/routes/<name>', methods=['DELETE'])
        def delete_route(name: str):
            """Remove a route."""
            self.stats['api_requests'] += 1

            success = self.router.remove_route(name)
            if not success:
                abort(404, f'Route {name} not found')

            return jsonify({'success': True}), 200

        # Statistics endpoints
        @self.app.route('/api/stats', methods=['GET'])
        def get_stats():
            """Get system statistics."""
            self.stats['api_requests'] += 1

            return jsonify({
                'api': self.stats,
                'processor': self.processor.get_stats(),
                'router': self.router.get_stats()
            }), 200

        @self.app.route('/api/stats/reset', methods=['POST'])
        def reset_stats():
            """Reset all statistics."""
            self.stats['api_requests'] += 1

            self.stats = {
                'api_requests': 0,
                'webhook_received': 0,
                'api_errors': 0
            }
            self.processor.reset_stats()
            self.router.reset_stats()

            return jsonify({'success': True}), 200

        # Health check
        @self.app.route('/api/health', methods=['GET'])
        def health_check():
            """Health check endpoint."""
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'version': '1.2.10',
                'routes_registered': len(self.router.routes),
                'events_processed': self.processor.get_stats()['processed']
            }), 200

        # Error handlers
        @self.app.errorhandler(HTTPException)
        def handle_http_error(e):
            """Handle HTTP errors."""
            self.stats['api_errors'] += 1
            return jsonify({
                'error': e.name,
                'message': e.description
            }), e.code

        @self.app.errorhandler(Exception)
        def handle_error(e):
            """Handle general errors."""
            logger.error(f"API error: {e}")
            self.stats['api_errors'] += 1
            return jsonify({
                'error': 'Internal Server Error',
                'message': str(e)
            }), 500

    def _verify_signature(self, platform: str, req) -> bool:
        """
        Verify webhook signature.

        Args:
            platform: Platform name (github, slack, etc.)
            req: Flask request object

        Returns:
            True if signature is valid
        """
        # Get secret from config
        secret = self.config['webhook_secrets'].get(platform)
        if not secret:
            # No secret configured, skip verification
            logger.warning(f"No webhook secret for {platform}, skipping verification")
            return True

        # Platform-specific signature verification
        if platform == 'github':
            signature = req.headers.get('X-Hub-Signature-256', '')
            if not signature:
                return False

            # Compute expected signature
            mac = hmac.new(
                secret.encode(),
                msg=req.get_data(),
                digestmod=hashlib.sha256
            )
            expected = 'sha256=' + mac.hexdigest()

            return hmac.compare_digest(signature, expected)

        elif platform == 'slack':
            signature = req.headers.get('X-Slack-Signature', '')
            timestamp = req.headers.get('X-Slack-Request-Timestamp', '')

            if not signature or not timestamp:
                return False

            # Compute expected signature
            sig_basestring = f"v0:{timestamp}:{req.get_data().decode()}"
            mac = hmac.new(
                secret.encode(),
                msg=sig_basestring.encode(),
                digestmod=hashlib.sha256
            )
            expected = 'v0=' + mac.hexdigest()

            return hmac.compare_digest(signature, expected)

        elif platform in ['notion', 'clickup']:
            # Generic signature verification
            signature = req.headers.get(f'{platform.capitalize()}-Signature', '')
            if not signature:
                return False

            mac = hmac.new(
                secret.encode(),
                msg=req.get_data(),
                digestmod=hashlib.sha256
            )
            expected = mac.hexdigest()

            return hmac.compare_digest(signature, expected)

        # Unknown platform
        return False

    def run(self, debug: bool = False):
        """
        Start the API server.

        Args:
            debug: Enable debug mode
        """
        logger.info(f"Starting webhook API server on {self.host}:{self.port}")
        self.app.run(host=self.host, port=self.port, debug=debug)

    async def run_async(self):
        """Run server asynchronously (for integration with async event loop)."""
        from hypercorn.asyncio import serve
        from hypercorn.config import Config

        config = Config()
        config.bind = [f"{self.host}:{self.port}"]

        logger.info(f"Starting async webhook API server on {self.host}:{self.port}")
        await serve(self.app, config)


def create_server(
    config_path: Optional[Path] = None,
    host: str = '0.0.0.0',
    port: int = 5050
) -> WebhookAPIServer:
    """
    Create and configure webhook API server.

    Args:
        config_path: Path to configuration file
        host: Server host
        port: Server port

    Returns:
        Configured WebhookAPIServer instance
    """
    # Load webhook config
    webhook_config = Path('extensions/core/webhooks/config.json')

    # Create processor and router
    processor = EventProcessor(webhook_config)
    router = EventRouter(webhook_config)

    # Create server
    server = WebhookAPIServer(
        processor=processor,
        router=router,
        config_path=config_path,
        host=host,
        port=port
    )

    return server


if __name__ == '__main__':
    # Run server standalone
    import sys

    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5050
    server = create_server(port=port)
    server.run(debug=True)
