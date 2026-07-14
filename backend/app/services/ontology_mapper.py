import json
from abc import ABC, abstractmethod
from typing import Dict, Optional
from pathlib import Path

from app.models.maintenance_schema import MaintenanceExtraction


class BaseOntologyProvider(ABC):
   
    @abstractmethod
    def get_canonical_name(self, field_name: str, alias: str) -> str:
        
        pass


class JSONOntologyProvider(BaseOntologyProvider):
   
    
    def __init__(self, ontology_dir: str):
        self.ontology_dir = Path(ontology_dir)
       
        self._dictionaries: Dict[str, Dict[str, str]] = {}
        self._load_dictionaries()
        
    def _load_dictionaries(self) -> None:
      
        if not self.ontology_dir.exists():
            return
            
      
        file_mapping = {
            "asset_type": "asset_types.json",
            "component": "components.json",
            "failure_mode": "failure_modes.json",
            "root_cause": "causes.json",
            "maintenance_action": "maintenance_actions.json",
            "severity": "severity.json",
        }
        
        for field, filename in file_mapping.items():
            filepath = self.ontology_dir / filename
            if filepath.exists():
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        self._dictionaries[field] = json.load(f)
                except Exception as e:
                    print(f"Error loading {filepath}: {e}")
            else:
                self._dictionaries[field] = {}

    def get_canonical_name(self, field_name: str, alias: str) -> str:
        if not alias or field_name not in self._dictionaries:
            return alias
            
        mapping = self._dictionaries[field_name]
        return mapping.get(alias, alias)


class OntologyMapper:
    
    
    def __init__(self, provider: BaseOntologyProvider):
        self.provider = provider

        self.mapped_fields = [
            "asset_type",
            "component",
            "failure_mode",
            "root_cause",
            "maintenance_action",
            "severity"
        ]
        
    def map_extraction(self, extraction: MaintenanceExtraction) -> MaintenanceExtraction:
        
        updates = {}
        
        for field in self.mapped_fields:
            original_value = getattr(extraction, field, None)
            if original_value is not None:
                mapped_value = self.provider.get_canonical_name(field, original_value)
                updates[field] = mapped_value
                
        
        return extraction.model_copy(update=updates)
