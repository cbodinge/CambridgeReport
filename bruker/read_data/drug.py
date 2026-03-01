from __future__ import annotations
from lxml import etree
from .ion import Ion


# noinspection PyProtectedMember
class Drug:
    """
    Drug Level Info Class
    """

    def __init__(self, drug: etree._Element):
        self._root = drug
        self.determination_id = drug.attrib['id']
        self.analyte_id = drug.attrib['analyteId']
        self.quant_ion_id = drug.attrib['quantificationIonParameterId']
        self.mass_error_score = drug.attrib['combinedMassErrorScore']
        self.sigma_score = drug.attrib['combinedSigmaScore']
        self.rt_score = drug.attrib['combinedRetentionTimeScore']
        self.qualifier_score = drug.attrib['qualifierScore']
        self.ccs_score = drug.attrib['combinedCcsScore']
        self.score = drug.attrib['score']
        self.ions = self._set_ions()

    def _set_ions(self):
        ions = self._root.xpath('ionCompounds//ionCompound')
        return [Ion(ion) for ion in ions]
