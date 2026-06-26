from flask import Flask, jsonify, request  # request for query parameters
import sys
import threading
from sensors import SensorManager, RealSensorProvider, AssignmentsManager
from dataReceiver import get_sensors, uds_client


def create_app(config_name='default', mock=False):
    app = Flask(__name__)
    
    @app.after_request
    def add_cors_headers(response):
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
    
    # Initialize SensorManager
    sensor_manager = SensorManager(mock=mock)
    app.sensor_manager = sensor_manager
    
    @app.route('/api/scan')
    def scan():
        print("🔍 Scanning for sensors...")
        # Return sensors from data received via Unix socket
        sensors = get_sensors()
        print(f"📡 Sensors in data store: {[s.get('sensorId') for s in sensors]}")
        return jsonify([{"id": s.get("sensorId")} for s in sensors])
    
    @app.route('/api/temps')
    def temps():
        # Return sensor data from socket: sensorId, temperature, alarmCode
        sensors = get_sensors()
        print(f"🌡️ /api/temps called, sensors raw data: {sensors}")
        temps_dict = {
            "sensors": [
                {
                    "sensorId": s.get("sensorId"),
                    "temperature": s.get("temperature"),
                    "alarmCode": s.get("alarmCode")
                }
                for s in sensors
            ]
        }
        print(f"🌡️ Returning temps_dict: {temps_dict}")
        return jsonify(temps_dict)
    
    @app.route('/api/switch-provider')
    def switch_provider():
        provider_type = request.args.get('type', 'real')  # Switch between mock and real sensor provider
        if provider_type == 'mock':
            app.sensor_manager.set_provider(SensorManager(mock=True).provider)
            return jsonify({"status": "mock"})
        else:
            app.sensor_manager.set_provider(RealSensorProvider())
            return jsonify({"status": "real"})
        
    @app.route('/api/assignments')
    def get_assignments():
        return jsonify(app.assignments_manager.get())

    @app.route('/api/assignments', methods=['POST'])
    def save_assignments():
        data = request.json
        app.assignments_manager.set(data)
        return jsonify({"status": "saved"})

    # Initialize AssignmentsManager in create_app()
    assignments_manager = AssignmentsManager()
    app.assignments_manager = assignments_manager
    
    return app

if __name__ == '__main__':
    mock = '--mock' in sys.argv
    debug = '--debug' in sys.argv
    app = create_app(mock=mock)
    print("🚀 Backend running:", "MOCK MODE" if mock else "REAL SENSORS")
    print("🐛 Debug mode:", "ON" if debug else "OFF")
    print("📱 Phone access: http://192.168.1.xxx:5000")  # Replace with your local IP
    
    # Connect to C++ UDS server in background thread
    socket_path = "/tmp/silo-monitor.sock" if mock else "/run/silo-monitor.sock"
    print(f"🔌 Connecting to C++ UDS server on {socket_path}...")
    threading.Thread(target=uds_client, args=(mock,), daemon=True).start()
    
    # Bind to 0.0.0.0 to make backend accessible from other devices
    app.run(host='0.0.0.0', port=5000, debug=debug,use_reloader=False)
