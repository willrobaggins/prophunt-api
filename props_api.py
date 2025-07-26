from flask import Flask, request, jsonify
import redis
import json

app = Flask(__name__)

r = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

@app.route('/prop-hunters/<username>', methods=['POST'])
def add_user(username):
        data = request.get_json()
        hiding = data.get('hiding', False)
        model_id = data.get('modelID', 0)
        orientation = data.get('orientation', 0)

        user_data = {
                'username': username,
                'hiding': hiding,
                'modelID': model_id,
                'orientation': orientation
        }
        r.set(username, json.dumps(user_data))
        return jsonify({"message": "User data added successfully!"}), 200

@app.route('/prop-hunters/<username>', methods=['GET'])
def get_user(username):
        response_data = []

        for user in username.split(','):
                user = user.strip()
                user_data = r.get(user)

                if user_data:
                        response_data.append(json.loads(user_data))
                else:
                        response_data.append({"username": user, "error": "User not found"})

        return jsonify(response_data), 200