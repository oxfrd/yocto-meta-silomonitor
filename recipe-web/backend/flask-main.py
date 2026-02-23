# from flask import Flask, jsonify
# from flask_cors import CORS

# app = Flask(__name__)
# CORS(app)


def staticSensors():
    sensors = [
        {"id": "28ff123456789abc", "name": "5m", "temp": 22.5, "position": 5, "assigned": True},
        {"id": "28ff123456789def", "name": "3m", "temp": 21.1, "position": 3, "assigned": True},
        {"id": "28ff123456789ghi", "name": "1m", "temp": 19.8, "position": 1, "assigned": True},
        {"id": "28ff123456789xyz", "name": "ambient", "temp": 17.3, "position": 0, "assigned": True}
    ]
    # Return list sorted by position (5,3,1,0)
    sensors = sorted(sensors, key=lambda s: s.get('position', -1), reverse=True)
    return jsonify(sensors)

# if __name__ == '__main__':
#     app.run(debug=True)
    
    
   ###### ///
   
from flask import Flask, jsonify
from flask_cors import CORS

def create_app(config_name='default'):
    app = Flask(__name__)
    # app.config.from_object(config[config_name])
    CORS(app)
    
    # # Inicjalizacja managera sensorów
    # sensor_manager = SensorManager(app.config)
    # app.sensor_manager = sensor_manager
    
    @app.route('/api/scan')
    def scan():
        return staticSensors()
    
    # @app.route('/api/assign', methods=['POST'])
    # def assign():
    #     data = request.get_json()
    #     success = sensor_manager.assign_sensor(
    #         data['id'], data['name'], data['position'],
    #         data.get('alarm_min'), data.get('alarm_max')
    #     )
    #     return jsonify({'success': success})
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
