from __future__ import annotations
from lxml import etree
import base64
import numpy as np


# noinspection PyProtectedMember
class Chromatogram:
    """
    Chromatogram Level Info Class
    """

    def __init__(self, chromatogram: etree._Element):
        self._root = chromatogram
        self.chromatogram_id = chromatogram.get('id')
        self.x = self.decode(chromatogram.get('retentionTimes'))
        self.y = self.decode(chromatogram.get('intensities'))

        self.beg = 0
        self.end = 0

    @staticmethod
    def decode(x: str):
        raw = base64.b64decode(x)
        return np.frombuffer(raw, dtype='>f8')  # little-endian float64
