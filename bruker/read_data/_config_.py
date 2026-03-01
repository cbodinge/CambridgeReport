from pathlib import Path
from lxml.etree import parse, _ElementTree
from ._open_file_ import recover_zip_streaming

HOME = Path(__file__).parent.parent.parent.absolute()
XML_PATH = HOME / 'bruker/read_data/recovered'


def open_xml(path: Path) -> _ElementTree:
    """

    Args:
        path: path to the XML file

    Returns: an etree object of the parsed XML file

    """
    with path.open(mode='r') as file:
        return parse(file)


def _open(pattern: str) -> _ElementTree:
    """Parses a desired XML into an etree object.

    Finds the XML file matching the pattern with the largest replicate number and parses it into an etree object.

    Args:
        pattern: The established Bruker file pattern

    Returns: an etree object of the parsed XML file

    """

    options = [file for file in XML_PATH.iterdir() if pattern in file.name]
    options.sort(reverse=True, key=lambda x: x.name)
    file = options[0]
    return open_xml(file)


CHROMS: _ElementTree|None = None
RESULTS: _ElementTree|None = None


def set_trees(path: Path) -> None:
    """
    Sets the global variables CHROMS and RESULTS based on the path given. The path should point to a .brkrar file.

    Args:
        path: a Path object pointing to a .brkrar file.

    Returns: None

    Raises: ValueError if the path does not point to a .brkrar file.

    """
    if path.suffix != '.brkrar':
        raise ValueError('Path must point to a .brkrar file.')

    recover_zip_streaming(str(path))

    global CHROMS, RESULTS
    CHROMS = _open('de.bdal.cdr.server.entity.Chromatogram')
    RESULTS = _open('de.bdal.tsq.server.entity.AnalysisResult')
    pass

