# Main routes blueprint
# Maintained by Sunny Aiden (sangsunlee.aiden@gmail.com)

from flask import Blueprint, jsonify

main = Blueprint('main', __name__)

@main.route('/api/info')
def api_info():
    return jsonify({
        'project': 'TEPIS',
        'maintainer': 'Sunny Aiden',
        'email': 'sangsunlee.aiden@gmail.com',
        'message': 'Welcome to the TEPIS Flask backend!'
    })