from datetime import datetime
from lxml import etree
from .drug import Drug


# noinspection PyProtectedMember
class Sample:
    def __init__(self, sample: etree._Element):
        self._root = sample
        self.analysis_result_id = sample.attrib['id']
        self.analysis_id = sample.attrib['analysisId']
        self.sample_id = sample.attrib['sampleId']
        self.operator = sample.attrib['instrumentOperator']
        self.instrument_sn = sample.attrib['instrumentSerialNumber']
        self.calibration_id = sample.attrib['calibrationFk']
        self.created_at = datetime.fromisoformat(sample.attrib['creationDate'])
        self.drugs = self._set_drugs()

    def _set_drugs(self):
        drugs = self._root.xpath('determinations//determination')
        return [Drug(drug) for drug in drugs]
