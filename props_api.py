from flask import Flask, request, jsonify
import redis
import json
import time

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024

r = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

TTL = 30 * 24 * 60 * 60
MAX_NAME_LENGTH = 32
MAX_NAMES = 100
RATE_LIMIT = 600
RATE_WINDOW = 60

def valid_name(name):
        return 0 < len(name) <= MAX_NAME_LENGTH and ':' not in name and ',' not in name

def normalize(name):
        return name.replace(' ', ' ').replace('_', ' ').strip().lower()

def player_key(name):
        return f"player:{normalize(name)}"

def is_int(value):
        return isinstance(value, int) and not isinstance(value, bool)

def get_player(name):
        key = player_key(name)
        data = r.getex(key, ex=TTL)
        if data is None:
                data = r.get(name)
                if data is None:
                        return None
                r.set(key, data, ex=TTL)
                r.delete(name)
        return data

@app.before_request
def check_rate_limit():
        key = f"rate:props:{request.remote_addr}:{int(time.time() // RATE_WINDOW)}"
        count = r.incr(key)
        if count == 1:
                r.expire(key, RATE_WINDOW)
        if count > RATE_LIMIT:
                return jsonify({"status": "error"}), 429

@app.route('/prop-hunters/<username>', methods=['POST'])
def add_user(username):
        username = username.strip()
        data = request.get_json(silent=True)
        if not valid_name(username) or not isinstance(data, dict):
                return jsonify({"status": "error"}), 400

        hiding = data.get('hiding', False)
        model_id = data.get('modelID', 0)
        orientation = data.get('orientation', 0)
        if not isinstance(hiding, bool) or not is_int(model_id) or not is_int(orientation):
                return jsonify({"status": "error"}), 400

        user_data = {
                'username': username,
                'hiding': hiding,
                'modelID': model_id,
                'orientation': orientation
        }
        r.set(player_key(username), json.dumps(user_data), ex=TTL)
        r.delete(username)
        return jsonify({"message": "User data added successfully!"}), 200

@app.route('/prop-hunters/<username>', methods=['GET'])
def get_user(username):
        users = [user.strip() for user in username.split(',')]
        if len(users) > MAX_NAMES:
                return jsonify({"status": "error"}), 400

        response_data = []
        for user in users:
                user_data = get_player(user) if valid_name(user) else None

                if user_data:
                        player = json.loads(user_data)
                        player['username'] = user
                        response_data.append(player)
                else:
                        response_data.append({"username": user, "error": "User not found"})

        return jsonify(response_data), 200
