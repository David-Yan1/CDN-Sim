from flask import Flask, request, jsonify
import json
from flask_cors import CORS
from cdn import run_simulation

app = Flask(__name__)
CORS(app)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/simulate')
def simulate():

    data = request.args.get('data')
    if data:
        try:
            json_data = json.loads(data)
            print(json_data)
        except json.JSONDecodeError:
            return 'Invalid JSON', 400

        # Process data
        numberOfUsers = json_data["numberOfUsers"]
        cachePolicy = json_data["cachePolicy"]
        cacheSize = json_data["cacheSize"]
        latency = json_data["latency"]
        rerouteRequests = json_data["rerouteRequests"]
        maxConcurrentRequests = json_data["maxConcurrentRequests"]
        coordinates = json_data["coordinates"]
        nodeCoordinates = json_data["nodeCoordinates"]

        results = run_simulation(coordinates=coordinates, node_coordinates=nodeCoordinates, number_of_users=numberOfUsers, cache_policy=cachePolicy, cache_size=cacheSize, latency=latency, max_concurrent_requests=maxConcurrentRequests, reroute_requests=rerouteRequests)

        return  jsonify(results), 200
    else:
        return 'No data provided', 400

if __name__ == '__main__':
    app.run(debug=True)