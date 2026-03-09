"""
Moduł sensorów DS18B20 - testowalny/mockowalny
"""
import glob
import os
from typing import Dict, List, Optional
from abc import ABC, abstractmethod
from dataclasses import dataclass
import json
import time

class AssignmentsManager:
    def __init__(self, storage_file="silo_assignments.json"):
        self.storage_file = storage_file
        self.assignments = self._load()
    
    def _load(self):
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {'5m': None, '3m': None, '1m': None, 'ambient': None}
    
    def _save(self):
        with open(self.storage_file, 'w') as f:
            json.dump(self.assignments, f)
    
    def get(self):
        return self.assignments.copy()
    
    def set(self, assignments):
        self.assignments = assignments
        self._save()

@dataclass
class SensorData:
    id: str
    temp: Optional[float] = None

class SensorInterface(ABC):
    """Interface dla providera sensorów"""
    @abstractmethod
    def scan(self) -> List[str]:
        pass
    
    @abstractmethod
    def get_temps(self) -> Dict[str, float]:
        pass

class RealSensorProvider(SensorInterface):
    """Prawdziwe sensory DS18B20"""
    
    def __init__(self, sensor_path: str = "/sys/bus/w1/devices"):
        self.sensor_path = sensor_path
    
    def scan(self) -> List[str]:
        """Zwraca listę adresów sensorów"""
        try:
            # Szukaj wszystkich folderów zaczynających się od 28-
            sensors = []
            for path in glob.glob(f"{self.sensor_path}/28-*"):
                sensor_id = os.path.basename(path)  # np. "28-0000090a1acd"
                sensors.append(sensor_id)
            print(f"🔍 Znalezione sensory: {sensors}")
            return sensors
        except Exception as e:
            print(f"❌ Błąd skanowania: {e}")
            return []
    
    def get_temps(self) -> Dict[str, float]:
        """Zwraca {sensor_id: temperatura}"""
        temps = {}
        for sensor_id in self.scan():
            temp = self._read_temp(sensor_id)
            if temp is not None:
                temps[sensor_id] = temp
                print(f"✅ {sensor_id}: {temp}°C")
            else:
                print(f"⚠️ {sensor_id}: Brak odczytu")
        return temps
    
    def _read_temp(self, sensor_id: str) -> Optional[float]:
        """Czyta temperaturę z danego sensora"""
        try:
            # sensor_id = "28-0000090a1acd"
            w1_slave_path = f"{self.sensor_path}/{sensor_id}/w1_slave"
            print(f"📖 Czytam: {w1_slave_path}")
            
            with open(w1_slave_path, 'r') as f:
                lines = f.readlines()
            
            if len(lines) > 1 and 'YES' in lines[0]:
                # Linia 2: "t=22500" (w tysiącznych °C)
                temp_line = lines[1]
                if 't=' in temp_line:
                    temp_raw = int(temp_line.split('t=')[1].strip())
                    return round(temp_raw / 1000.0, 2)
            else:
                print(f"⚠️ {sensor_id}: CRC failed")
        except FileNotFoundError:
            print(f"❌ Plik nie znaleziony: {w1_slave_path}")
        except Exception as e:
            print(f"❌ Błąd odczytu {sensor_id}: {e}")
        
        return None

class MockSensorProvider(SensorInterface):
    def __init__(self):
        self.global_time = time.time()
    
    def scan(self) -> List[str]:
        return [
            "28ff123456789abc",
            "28ffabcdef123456", 
            "28ffaabbccddeeff",
            "28ff001122334455"
        ]
    
    def get_temps(self) -> Dict[str, float]:
        # Jeden globalny czas dla WSZYSTKICH urządzeń
        self.global_time += 2  # Symuluj 2s odstępy
        
        import random
        temps = {
            "28ff123456789abc": round(22.5 + random.uniform(-0.2, 0.2), 1),
            "28ffabcdef123456": round(21.1 + random.uniform(-0.2, 0.2), 1),
            "28ffaabbccddeeff": round(19.8 + random.uniform(-0.2, 0.2), 1),
            "28ff001122334455": round(17.3 + random.uniform(-0.1, 0.1), 1)
        }
        print(f"🌐 Global time: {self.global_time}, temps: {temps}")
        return temps

class SensorManager:
    """Manager sensorów z możliwością przełączania providera"""
    
    def __init__(self, provider: SensorInterface = None, mock: bool = False):
        if mock:
            self.provider = MockSensorProvider()
        elif provider:
            self.provider = provider
        else:
            self.provider = RealSensorProvider()
    
    def scan(self) -> List[SensorData]:
        """Skanuj sensory"""
        ids = self.provider.scan()
        return [SensorData(id=id) for id in ids]
    
    def get_temps(self) -> Dict[str, float]:
        """Pobierz temperatury"""
        return self.provider.get_temps()
    
    def set_provider(self, provider: SensorInterface):
        """Zmień provider w runtime"""
        self.provider = provider
