# app/schemas/base.py

from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class TimestampedModel(BaseModel):
    criado_em: datetime
    atualizado_em: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)