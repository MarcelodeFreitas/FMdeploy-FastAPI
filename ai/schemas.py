from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AI(BaseModel):
    id: int
    title: str
    description: Optional[str]
    python_script_name: str
    python_script_path: str
    output_type: str
    is_private: bool
    created_in: datetime