# TODO: convert from Flask to FastAPI

from flask import Flask, request, jsonify
import redis
import pickle

app = Flask(__name__)
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# TODO: add an update endpoint

@app.route('/register_agent', methods=['POST'])
def register_agent():
    agent_info = request.get_json()
    serialized_agent_info = pickle.dumps(agent_info)
    redis_client.set(agent_info["agent_id"], serialized_agent_info)
    return jsonify({"status": "success", "agent_id": agent_info["agent_id"]})

@app.route('/search_agent', methods=['GET'])
def search_agent():
    agent_id = request.args.get('agent_id')
    capability = request.args.get('capability')

    if agent_id:
        serialized_agent_info = redis_client.get(agent_id)
        if not serialized_agent_info:
            return jsonify({"status": "error", "message": "Agent not found."}), 404
        agent_info = pickle.loads(serialized_agent_info)
        return jsonify(agent_info)

    elif capability:
        matching_agents = []
        for agent_id in redis_client.keys():
            serialized_agent_info = redis_client.get(agent_id)
            agent_info = pickle.loads(serialized_agent_info)
            if capability in agent_info["capabilities"]:
                matching_agents.append(agent_info)
        if not matching_agents:
            return jsonify({"status": "error", "message": "No agents found with the specified capability."}), 404
        return jsonify(matching_agents)

    else:
        return jsonify({"status": "error", "message": "Specify agent_id or capability for searching."}), 400

if __name__ == "__main__":
    app.run(debug=True)