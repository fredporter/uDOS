"""
uDOS Dashboard POKE Handler
Manages memory operations and real-time monitoring
"""

from flask import Blueprint, jsonify
from flask_socketio import Namespace, emit
import threading
import time

class POKENamespace(Namespace):
    def __init__(self, namespace=None):
        super().__init__(namespace)
        self.memory = [0] * 65536  # 64K memory space
        self.watchers = {}
        self.watch_thread = None
        self.running = False
        self.start_watch_thread()

    def on_connect(self):
        """Handle client connection"""
        print("Client connected to POKE namespace")

    def on_disconnect(self):
        """Handle client disconnection"""
        print("Client disconnected from POKE namespace")

    def on_poke(self, data):
        """Handle POKE command"""
        address = data.get('address')
        value = data.get('value')

        if not self.is_valid_address(address) or not self.is_valid_value(value):
            return {'error': 'Invalid POKE parameters'}

        self.memory[address] = value
        emit('memory_update', {'address': address, 'value': value}, broadcast=True)
        return {'status': 'success'}

    def on_peek(self, data):
        """Handle PEEK command"""
        address = data.get('address')

        if not self.is_valid_address(address):
            return {'error': 'Invalid PEEK address'}

        return {'value': self.memory[address]}

    def on_watch(self, data):
        """Set up memory watch"""
        address = data.get('address')
        threshold = data.get('threshold', 0)
        interval = data.get('interval', 1000)

        if not self.is_valid_address(address):
            return {'error': 'Invalid watch address'}

        self.watchers[address] = {
            'threshold': threshold,
            'interval': interval,
            'last_value': self.memory[address]
        }

        return {'status': 'success'}

    def on_clear_watch(self, data):
        """Clear memory watch"""
        address = data.get('address')
        if address in self.watchers:
            del self.watchers[address]
        return {'status': 'success'}

    def start_watch_thread(self):
        """Start the watch monitoring thread"""
        if self.watch_thread is None:
            self.running = True
            self.watch_thread = threading.Thread(target=self.watch_loop)
            self.watch_thread.daemon = True
            self.watch_thread.start()

    def stop_watch_thread(self):
        """Stop the watch monitoring thread"""
        self.running = False
        if self.watch_thread:
            self.watch_thread.join()
            self.watch_thread = None

    def watch_loop(self):
        """Monitor memory watches"""
        while self.running:
            for address, watch in list(self.watchers.items()):
                current_value = self.memory[address]
                if abs(current_value - watch['last_value']) >= watch['threshold']:
                    emit('watch_trigger', {
                        'address': address,
                        'value': current_value,
                        'previous': watch['last_value']
                    }, broadcast=True)
                    watch['last_value'] = current_value
            time.sleep(0.1)  # Check watches every 100ms

    @staticmethod
    def is_valid_address(address):
        """Validate memory address"""
        return isinstance(address, int) and 0 <= address <= 65535

    @staticmethod
    def is_valid_value(value):
        """Validate memory value"""
        return isinstance(value, int) and 0 <= value <= 255

# Blueprint for REST endpoints
poke_bp = Blueprint('poke', __name__)

@poke_bp.route('/memory/<int:address>', methods=['GET'])
def peek_memory(address):
    """REST endpoint for PEEK"""
    if not POKENamespace.is_valid_address(address):
        return jsonify({'error': 'Invalid address'}), 400

    # Access memory through SocketIO namespace
    socketio = poke_bp.config['socketio']
    poke_ns = socketio.namespace_handlers.get('/poke')

    if not poke_ns:
        return jsonify({'error': 'POKE system not initialized'}), 500

    return jsonify({'value': poke_ns.memory[address]})

@poke_bp.route('/memory/<int:address>/<int:value>', methods=['POST'])
def poke_memory(address, value):
    """REST endpoint for POKE"""
    if not POKENamespace.is_valid_address(address):
        return jsonify({'error': 'Invalid address'}), 400
    if not POKENamespace.is_valid_value(value):
        return jsonify({'error': 'Invalid value'}), 400

    # Access memory through SocketIO namespace
    socketio = poke_bp.config['socketio']
    poke_ns = socketio.namespace_handlers.get('/poke')

    if not poke_ns:
        return jsonify({'error': 'POKE system not initialized'}), 500

    poke_ns.memory[address] = value
    socketio.emit('memory_update', {'address': address, 'value': value}, namespace='/poke')

    return jsonify({'status': 'success'})

def init_poke(app, socketio):
    """Initialize POKE system"""
    socketio.on_namespace(POKENamespace('/poke'))
    app.register_blueprint(poke_bp, url_prefix='/api/poke')
    poke_bp.config = {'socketio': socketio}
