from __future__ import annotations
from lxml import etree


from .chromatogram import Chromatogram
from . import _config_ as c


# noinspection PyProtectedMember
class Ion:
    """
    Ion Level Info Class
    """

    def __init__(self, ion: etree._Element):
        self.ion_id = ion.attrib['id']
        self.ion_parameter_set_id = ion.attrib['ionParameterSetId']
        self.rt = float(ion.attrib['retentionTimeInMin'])
        self.area = float(ion.attrib['peakArea'])
        self.height = float(ion.attrib['peakHeight'])
        self.intensity = float(ion.attrib['peakIntensity'])
        self.mz = float(ion.attrib['moz'])
        self.mass_error_score = ion.attrib['massErrorScore']
        self.rt_score = ion.attrib['retentionTimeScore']
        self.sigma_score = ion.attrib['sigmaScore']
        self.formula = ion.attrib['sumFormula']
        self.charge_state = ion.attrib['chargeState']
        self.ms_width = ion.attrib['msWidth']
        self.sn = float(ion.attrib['signalToNoise'])
        self.baseline_intensity = float(ion.attrib['baseLineIntensity'])
        self.compound_id = ion.attrib['compoundId']
        self.chromatogram_id = ion.attrib['chromatogramId']
        self.spectrum_id = ion.attrib['spectrumId']
        self.ms_intensity = float(ion.attrib['msIntensity'])
        self.peak_start = float(ion.attrib['peakStartTime'])
        self.peak_end = float(ion.attrib['peakEndTime'])
        self.peak_width = float(ion.attrib['peakWidthMinutes'])

        self.chromatogram = self.get_chromatogram()

    def get_chromatogram(self):
        if c.CHROMS:
            chrom = c.CHROMS.xpath(f"chromtograms//chromatogram[@id='{self.chromatogram_id}']")
            if chrom:
                return Chromatogram(chrom[0])

        return None
