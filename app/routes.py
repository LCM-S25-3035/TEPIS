# Main routes blueprint
# Maintained by Sunny Aiden (sangsunlee.aiden@gmail.com)

from flask import Blueprint, jsonify

main = Blueprint('main', __name__)
@main.route('/api/health', methods=['GET'])
def api_health():
    return jsonify({
        'status': 'healthy'
    })
@main.route('/api/status', methods=['GET'])
def api_status():
    return jsonify({
        'status': 'running',
        'version': '1.0.0'
    })