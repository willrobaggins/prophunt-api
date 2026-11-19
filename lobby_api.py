from flask import Flask, request, jsonify
import json
import redis
import time

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024

r = redis.Redis(host='localhost', port=6379, db=0)

TTL = 30 * 24 * 60 * 60
MAX_NAME_LENGTH = 32
MAX_LIST_LENGTH = 200
MAX_ENTRY_LENGTH = 4096
RATE_LIMIT = 600
RATE_WINDOW = 60

def valid_name(name):
        return 0 < len(name) <= MAX_NAME_LENGTH and ':' not in name

def valid_list(data):
        if not isinstance(data, list) or len(data) > MAX_LIST_LENGTH:
                return False
        return all(entry is None or (isinstance(entry, str) and len(entry) <= MAX_ENTRY_LENGTH) for entry in data)

def get_list(prefix, lobby_id):
        return r.getex(f"{prefix}:{lobby_id}", ex=TTL)

def set_list(prefix, lobby_id, data):
        r.set(f"{prefix}:{lobby_id}", json.dumps(data), ex=TTL)

@app.before_request
def check_rate_limit():
        key = f"rate:lobby:{request.remote_addr}:{int(time.time() // RATE_WINDOW)}"
        count = r.incr(key)
        if count == 1:
                r.expire(key, RATE_WINDOW)
        if count > RATE_LIMIT:
                return jsonify({"status": "error"}), 429

@app.route('/lobbies/<lobby_id>', methods=['POST'])
def add_lobby(lobby_id):
        data = request.get_json(silent=True)
        if not valid_name(lobby_id) or not valid_list(data):
                return jsonify({"status": "error"}), 400
        set_list("lobby", lobby_id, data)
        return jsonify({"message": "Lobby data added successfully!"}), 200

@app.route('/lobbies/<lobby_id>', methods=['GET'])
def get_lobby(lobby_id):
        lobby_data = get_list("lobby", lobby_id) if valid_name(lobby_id) else None
        if lobby_data:
                lobby = json.loads(lobby_data)
                return jsonify(lobby), 200
        else:
                return jsonify({"status": "error"}), 404

@app.route('/lobby_seekers/<lobby_id>', methods=['POST'])
def post_seekers(lobby_id):
        data = request.get_json(silent=True)
        if not valid_name(lobby_id) or not valid_list(data):
                return jsonify({"status": "error"}), 400
        set_list("lobby_seekers", lobby_id, data)
        return jsonify({"message": "Lobby seeker data added successfully!"}), 200

@app.route('/lobby_seekers/<lobby_id>', methods=['GET'])
def get_seekers(lobby_id):
        seeker_data = get_list("lobby_seekers", lobby_id) if valid_name(lobby_id) else None
        if seeker_data:
                seekers = json.loads(seeker_data)
                return jsonify(seekers), 200
        else:
                return jsonify({"status": "error"}), 404
