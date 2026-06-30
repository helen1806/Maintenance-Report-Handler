from pydantic import BaseModel
from typing import Optional

class MaintenanceExtraction(BaseModel):
    asset: str
    asset_type: Optional[str] = None
    component: Optional[str] = None
    failure_mode: Optional[str] = None
    root_cause: Optional[str] = None
    severity: Optional[str] = None
    maintenance_action: Optional[str] = None
    location: Optional[str] = None
    confidence: Optional[float] = None