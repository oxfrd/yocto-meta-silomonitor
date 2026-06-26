import os
import socket
import struct
import threading
import time
from flask import Flask, jsonify
import snapshot_pb2

def _get_socket_path(mock=False):
    if mock:
        print("[UDS] Using mock socket path")
        return "/tmp/silo-monitor.sock"
    return "/run/silo-monitor.sock"


data_store = {"sensors": []}
lock = threading.Lock()

def _read_exact(fd, size):
    buffer = b''
    while len(buffer) < size:
        chunk = fd.recv(size - len(buffer))
        if not chunk:
            return None
        buffer += chunk
    return buffer


def _parse_snapshot(raw):
    snapshot = snapshot_pb2.MonitoringSnapshot()
    snapshot.ParseFromString(raw)
    sensors = []
    for sensor in snapshot.sensors:
        sensor_data = {
            "sensorId": sensor.sensor_id,
            "temperature": sensor.temperature if sensor.HasField("temperature") else None,
            "alarmCode": sensor.alarm_code if sensor.HasField("alarm_code") else None,
        }
        sensors.append(sensor_data)
    return sensors


def uds_client(mock=False):
    """Poll C++ UDS server every 5 seconds for sensor data"""
    while True:
        try:
            # Connect to C++ server
            fd = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            fd.settimeout(3)  # 3 second timeout

            try:
                socket_path = _get_socket_path(mock=mock)
                fd.connect(socket_path)

                raw_len = _read_exact(fd, 4)
                if raw_len is None:
                    print("[UDS] ❌ No length prefix received")
                else:
                    msg_len = struct.unpack("!I", raw_len)[0]
                    raw = _read_exact(fd, msg_len)
                    if raw is None or len(raw) != msg_len:
                        print(f"[UDS] ❌ Incomplete message: expected {msg_len}, got {len(raw) if raw is not None else 0}")
                    else:
                        try:
                            sensors = _parse_snapshot(raw)
                            with lock:
                                data_store["sensors"] = sensors
                            print(f"[UDS] 📡 {len(sensors)} sensors")
                            print(f"[UDS] Sample sensor: {sensors[0] if sensors else 'EMPTY'}")
                        except Exception as e:
                            print(f"[UDS] ❌ Protobuf parse error: {e}")
                            print(f"[UDS] 📡 Raw message: {raw}")

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