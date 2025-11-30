# POKE Online Extension - Flask Server
from flask import Flask, jsonify, request, send_from_directory
import os

from .tunnel_manager import TunnelManager
from .sharing_manager import SharingManager
from .group_manager import GroupManager


app = Flask(__name__, static_folder='web')
tunnel_mgr = TunnelManager()
sharing_mgr = SharingManager()
group_mgr = GroupManager()


# Serve dashboard
@app.route('/')
def dashboard():
    return app.send_static_file('dashboard.html')


# Tunnel status
@app.route('/poke/status')
def poke_status():
    status = tunnel_mgr.get_status()
    return jsonify(status)


# Start a new tunnel
@app.route('/poke/start', methods=['POST'])
def poke_start():
    data = request.get_json(force=True)
    port = data.get('port', 5000)
    provider = data.get('provider')
    subdomain = data.get('subdomain')
    expires_hours = data.get('expires_hours')
    try:
        tunnel = tunnel_mgr.create_tunnel(
            port=port,
            provider=provider,
            subdomain=subdomain,
            expires_hours=expires_hours
        )
        return jsonify({'success': True, 'tunnel': tunnel.__dict__}), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


# Stop/close a tunnel
@app.route('/poke/stop', methods=['POST'])
def poke_stop():
    data = request.get_json(force=True)
    tunnel_id = data.get('tunnel_id')
    if not tunnel_id:
        return jsonify({'success': False, 'error': 'Missing tunnel_id'}), 400
    result = tunnel_mgr.close_tunnel(tunnel_id)
    return jsonify({'success': result})


# List all shares
@app.route('/poke/shares')
def poke_shares():
    shares = [s.to_dict() for s in sharing_mgr.list_shares()]
    return jsonify({'shares': shares})


# List all groups
@app.route('/poke/groups')
def poke_groups():
    groups = [g.to_dict() for g in group_mgr.groups.values()]
    return jsonify({'groups': groups})

# Create a new group
@app.route('/poke/groups', methods=['POST'])
def create_group():
    data = request.get_json(force=True)
    name = data.get('name')
    description = data.get('description', '')
    private = data.get('private', False)
    expires_hours = data.get('expires_hours')
    max_members = data.get('max_members', 10)
    try:
        group = group_mgr.create_group(
            name=name,
            description=description,
            private=private,
            expires_hours=expires_hours,
            max_members=max_members
        )
        return jsonify({'success': True, 'group': group.to_dict()}), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


if __name__ == '__main__':
    app.run(port=5050, debug=True)
