from __future__ import annotations

from datetime import datetime
from typing import List

from .sample import Sample
from .drug import Drug

class Batch:
    name: str
    operator: str
    station: str
    date: datetime
    path: str
    ms_method: str
    hplc_method: str
    samples: List[Sample]
    drugs: List[Drug]



