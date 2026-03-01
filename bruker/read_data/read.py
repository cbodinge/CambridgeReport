from .sample import Sample
from . import _config_ as c
from shutil import rmtree


def read(path: c.Path) -> list[Sample]:
    c.set_trees(path)
    samples = get_samples()

    if c.XML_PATH.exists():
        rmtree(c.XML_PATH)

    return samples


def get_samples() -> list[Sample]:
    """
    Reads the sample, drug, ion, and chromatogram information by walking through the analysisResult file.
    Chromatograms are retrieved from the Chromatogram file but in a directed way since each ion result has an associated chromatogram.

    Returns: A list of Sample objects.

    """
    if c.RESULTS:
        samples = c.RESULTS.xpath('analysisResults//analysisResult')
        return [Sample(sample) for sample in samples]

    return []
