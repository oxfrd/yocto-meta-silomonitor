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
            return [p.split('/')[-1].replace('-', '') 
                   for p in glob.glob(f"{self.sensor_path}/28*")]
        except:
            return []
    
    def get_temps(self) -> Dict[str, float]:
        """Zwraca {sensor_id: temperatura}"""
        temps = {}
        for sensor_id in self.scan():
            temp = self._read_temp(sensor_id)
            if temp is not None:
                temps[sensor_id] = temp
        return temps
    
    def _read_temp(self, sensor_id: str) -> Optional[float]:
        try:
            path = f"{self.sensor_path}/28-{sensor_id[2:]}"
            with open(path, 'r') as f:
                lines = f.readlines()
            if len(lines) > 1 and 'YES' in lines[0]:
                temp_str = lines[1].split('t=')[1]
                return float(temp_str) / 1000.0
        except:
            pass
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
