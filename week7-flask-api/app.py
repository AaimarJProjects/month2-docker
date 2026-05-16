from flask import Flask
from flask import request
from markupsafe import escape
import uuid


app = Flask(__name__)

users = {}

@app.route("/health")
def health():
    return "Health", 200

@app.route("/user", methods=['POST'])
def create_user():
    data = request.json
    user_id = str(uuid.uuid4())
    for key, value in users.items():
        if value.get('email') == data.get('email'):
            return "User already exists", 409
    
    users[user_id] = data
    return {"user_id": user_id, "data": data}, 200

 
@app.route("/user/<user_id>", methods=['DELETE'])
def delete_user(user_id):
    if user_id in users:
            del users[user_id]
            return "User deleted", 200
    return "User not found", 404


if __name__ =="__main__":
    app.run(host="0.0.0.0")
