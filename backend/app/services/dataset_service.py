import pandas as pd
from pathlib import Path
from typing import Dict, Any, List
import os

class DatasetService:
    def __init__(self, data_dir: str = None):
        # Resolve the data directory dynamically relative to this file
        if data_dir is None:
            # __file__ is backend/app/services/dataset_service.py
            # So parents[2] is backend/
            base_dir = Path(__file__).resolve().parents[2]
            self.data_dir = base_dir / "data" / "datasets"
        else:
            self.data_dir = Path(data_dir)
            
        self.datasets: Dict[str, pd.DataFrame] = {}
        self.zone_mapping = {
            "zone-1-nw": "dataset_zone_1_preprocessed.csv",
            "zone-2-ne": "dataset_zone_2_preprocessed.csv",
            "zone-4": "dataset_zone_4_preprocessed.csv",
            "zone-5": "dataset_zone_5_preprocessed.csv",
        }
        self._initialized = False

    def initialize(self):
        if self._initialized:
            return
        
        if not self.data_dir.exists():
            print(f"Warning: Dataset directory {self.data_dir} does not exist.")
            return

        for zone_id, filename in self.zone_mapping.items():
            file_path = self.data_dir / filename
            if file_path.exists():
                try:
                    df = pd.read_csv(file_path)
                    self.datasets[zone_id] = df
                except Exception as e:
                    print(f"Error loading {filename}: {e}")
            else:
                print(f"Warning: {filename} not found.")
                
        self._initialized = True

    def get_latest_reading(self, zone_id: str) -> Dict[str, Any]:
        """Get the most recent row of data for a specific zone."""
        if not self._initialized:
            self.initialize()
            
        if zone_id not in self.datasets:
            return None
            
        df = self.datasets[zone_id]
        if df.empty:
            return None
            
        latest = df.iloc[-1]
        return latest.to_dict()

    def get_zone_moisture(self, zone_id: str) -> float:
        reading = self.get_latest_reading(zone_id)
        if reading and 'soil_moisture' in reading:
            return float(reading['soil_moisture'])
        return 0.0

    def get_zone_temperature(self, zone_id: str) -> float:
        reading = self.get_latest_reading(zone_id)
        if reading and 'weather_temp' in reading:
            return float(reading['weather_temp'])
        return 0.0

    def get_metadata(self) -> Dict[str, Any]:
        if not self._initialized:
            self.initialize()
            
        metadata = {
            "total_zones": len(self.datasets),
            "zones": {}
        }
        for zone_id, df in self.datasets.items():
            metadata["zones"][zone_id] = {
                "rows": len(df),
                "columns": list(df.columns)
            }
        return metadata

# Singleton instance
_dataset_service_instance = None

def get_dataset_service() -> DatasetService:
    global _dataset_service_instance
    if _dataset_service_instance is None:
        _dataset_service_instance = DatasetService()
    return _dataset_service_instance
