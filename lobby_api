from flask import Flask, request, jsonify
import json
import redis

app = Flask(__name__)

r = redis.Redis(host='localhost', port=6379, db=0)

@app.route('/lobbies/<lobby_id>', methods=['POST'])
def add_lobby(lobby_id):
        data = request.get_json()
        r.set(f"lobby:{lobby_id}", json.dumps(data))
        return jsonify({"message": "Lobby data added successfully!"}), 200

@app.route('/lobbies/<lobby_id>', methods=['GET'])
def get_lobby(lobby_id):
        lobby_data = r.get(f"lobby:{lobby_id}")
        if lobby_data:
                lobby = json.loads(lobby_data)
                return jsonify(lobby), 200
        else:
                return jsonify({"status": "error"}), 400

@app.route('/lobby_seekers/<lobby_id>', methods=['POST'])
def post_seekers(lobby_id):
        data = request.get_json()
        r.set(f"lobby_seekers:{lobby_id}", json.dumps(data))
        return jsonify({"message": "Lobby seeker data added successfully!"}), 200

@app.route('/lobby_seekers/<lobby_id>', methods=['GET'])
def get_seekers(lobby_id):
        seeker_data = r.get(f"lobby_seekers:{lobby_id}")
        if seeker_data:
                seekers = json.loads(seeker_data)
                return jsonify(seekers), 200
        else:
                return jsonify({"status": "error"}), 400
