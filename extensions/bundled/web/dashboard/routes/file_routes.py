"""File browser routes for the dashboard"""

from . import app, file_service
from flask import jsonify, request

@app.route('/api/files/list')
def list_files():
    """List files in a directory"""
    try:
        path = request.args.get('path', '')
        items = file_service.list_directory(path)
        return jsonify({'status': 'success', 'items': items})
    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 403
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/files/content')
def get_file_content():
    """Get file content with preview"""
    try:
        path = request.args.get('path', '')
        content = file_service.get_file_content(path)
        if content is None:
            return jsonify({'status': 'error', 'message': 'File not found'}), 404
        return jsonify({'status': 'success', 'content': content})
    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 403
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
