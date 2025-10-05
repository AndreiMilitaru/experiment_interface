from datetime import datetime
import numpy as np
from typing import Optional, Dict
from .manager_interface import MZManagerInterface

class DummyMZManager(MZManagerInterface):
    def __init__(self, lock_check_interval: float = 0.1):
        self._monitoring = False
        self._setpoint = 0.0
        self._lock_check_interval = lock_check_interval
        
    def perform_range_calibration(self) -> Dict:
        return {
            'parameters': np.array([1.0, 2.0]),
            'covariance': np.array([[0.1, 0], [0, 0.1]]),
            'histogram': np.array([1, 2, 3]),
            'edges': np.array([0, 1, 2, 3]),
            'timestamp': datetime.now().isoformat()
        }
    
    def perform_visibility_calibration(self) -> Dict:
        return {
            'visibility': 0.95,
            'timestamp': datetime.now().isoformat()
        }
    
    def evaluate_current_lock(self) -> Dict:
        return {
            'lock_parameters': np.array([1.0, 0.1]),
            'lock_covariance': np.array([[0.01, 0], [0, 0.01]]),
            'histogram': np.array([1, 2, 3]),
            'edges': np.array([0, 1, 2, 3]),
            'timestamp': datetime.now().isoformat()
        }
    
    @property
    def latest_lock_quality(self) -> Optional[float]:
        return 0.9
    
    @property
    def setpoint(self) -> float:
        return self._setpoint
    
    @setpoint.setter
    def setpoint(self, value: float):
        self._setpoint = value
    
    def start_monitoring(self):
        self._monitoring = True
    
    def stop_monitoring(self):
        self._monitoring = False
    
    def save_current_pid_config(self):
        pass
    
    def load_latest_pid_config(self):
        pass
