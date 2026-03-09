from flask import Flask, jsonify, request  # request dla query params
import sys
from sensors import SensorManager, RealSensorProvider, AssignmentsManager


def create_app(config_name='default', mock=False):
    app = Flask(__name__)
    
    @app.after_request
    def add_cors_headers(response):
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
    
    # 🆕 Użyj SensorManager
    sensor_manager = SensorManager(mock=mock)
    app.sensor_manager = sensor_manager
    
    @app.route('/api/scan')
    def scan():
        sensors = app.sensor_manager.scan()
        return jsonify([{"id": s.id} for s in sensors])
    
    @app.route('/api/temps')
    def temps():
        temps_dict = app.sensor_manager.get_temps()
        return jsonify(temps_dict)
    
    @app.route('/api/switch-provider')
    def switch_provider():
        provider_type = request.args.get('type', 'real')  # ✅ Teraz request działa
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

    # Inicjalizacja w create_app():
    assignments_manager = AssignmentsManager()
    app.assignments_manager = assignments_manager
    
    return app

if __name__ == '__main__':
    mock = '--mock' in sys.argv
    app = create_app(mock=mock)
    print("🚀 Backend działa:", "MOCK MODE" if mock else "REAL SENSORS")
    print("📱 Telefon: http://192.168.1.xxx:5000")  # Twój lokalny IP!
    
    # 🆕 ZMIANA: 0.0.0.0 = DOSTĘPNE DLA TELEFONU
    app.run(host='0.0.0.0', port=5000, debug=True)
