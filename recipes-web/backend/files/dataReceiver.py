import os
import json
import socket
import threading
import time
from flask import Flask, jsonify

SOCK_PATH = "/run/silo-monitor.sock"
data_store = {"sensors": []}
lock = threading.Lock()

def uds_client():
    """Poll C++ UDS server every 5 seconds for sensor data"""
    while True:
        try:
            # Connect to C++ server
            fd = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            fd.settimeout(3)  # 3 second timeout
            
            try:
                fd.connect(SOCK_PATH)
                
                # Read data from socket
                raw = b''
                while True:
                    chunk = fd.recv(4096)
                    if not chunk:
                        break
                    raw += chunk
                    if b'\n' in raw:
                        break
                
                if raw:
                    try:
                        msg = json.loads(raw.decode("utf-8").strip())
                        with lock:
                            if isinstance(msg, list):
                                data_store["sensors"] = msg
                                print(f"[UDS] 📡 {len(msg)} sensors")
                                print(f"[UDS] Sample sensor: {msg[0] if msg else 'EMPTY'}")
                            else:
                                data_store.update(msg)
                    except json.JSONDecodeError as e:
                        print(f"[UDS] ❌ JSON error: {e}")
            
            except socket.timeout:
                print("[UDS] ⏱️ Timeout")
            except Exception as e:
                print(f"[UDS] ❌ {e}")
            finally:
                fd.close()
        
        except Exception as e:
            print(f"[UDS] Error: {e}")
        
        # Poll every 5 seconds
        time.sleep(5)

app = Flask(__name__)

def get_sensors():
    """Thread-safe getter for sensors list from data_store"""
    with lock:
        sensors = data_store.get("sensors", [])
        print(f"[GET_SENSORS] Returning {len(sensors)} sensors: {[s.get('sensorId') for s in sensors]}")
        return sensors

@app.route("/api/sensors")
def get_sensors_endpoint():
    with lock:
        sensors = data_store.get("sensors", [])
        print(f"[API] /api/sensors endpoint called, returning {len(sensors)} sensors")
        return jsonify(data_store)

if __name__ == "__main__":
    # Note: This file is imported by flask-main.py, not run directly
    # UDS client is started from flask-main.py
    print("[WARNING] dataReceiver.py should be imported, not run directly")
    app.run(host="0.0.0.0", port=5000)