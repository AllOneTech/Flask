import os
import redis
from flask import Flask, request, jsonify

app = Flask(__name__)

# Use Render's Redis URL from environment variables
redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')  # Default to localhost for local dev
redis_client = redis.Redis.from_url(redis_url, decode_responses=True)

@app.route('/execute', methods=['POST'])
def execute_code():
    try:
        code = request.json.get("code")
        sandbox_id = request.json.get("sandbox_id") or str(uuid.uuid4())
        sandbox_key = f"sandbox:{sandbox_id}"
        sandbox_env = redis_client.hgetall(sandbox_key)

        if not sandbox_env:
            sandbox_env = {}

        exec(code, {"__builtins__": None}, sandbox_env)
        redis_client.hmset(sandbox_key, sandbox_env)

        return jsonify({"sandbox_id": sandbox_id, "environment": sandbox_env})
    except Exception as e:
        return jsonify({"error": str(e)}), 400
