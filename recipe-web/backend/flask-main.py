from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/scan')
def scan():
    sensors = [
        {"id": "sensor1", "name": "5m", "temp": 22.5, "position": 5, "assigned": True},
        {"id": "sensor2", "name": "3m", "temp": 21.1, "position": 3, "assigned": True},
        {"id": "sensor3", "name": "1m", "temp": 19.8, "position": 1, "assigned": True},
        {"id": "ambient", "name": "Temperatura otoczenia", "temp": 17.3, "position": 0, "assigned": True}
    ]
    # Return list sorted by position (5,3,1,0)
    sensors = sorted(sensors, key=lambda s: s.get('position', -1), reverse=True)
    return jsonify(sensors)

if __name__ == '__main__':
    app.run(debug=True)