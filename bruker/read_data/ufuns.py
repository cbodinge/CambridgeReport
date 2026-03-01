from __future__ import annotations
from html import unescape as html_unescape
from typing import Union

from lxml import etree

XmlLike = Union[str, bytes]


def parse_escaped_xml(payload: XmlLike) -> etree._Element:
    """
    Parse XML that may contain escaped entities like '&#10;' before the root element.

    Strategy:
      1) Decode bytes safely.
      2) Unescape HTML/XML character references (turn '&#10;' into '\n', '&lt;' into '<', etc.).
      3) Trim leading BOM/whitespace.
      4) Parse with lxml.

    Returns:
      Root element.
    """
    if isinstance(payload, bytes):
        text = payload.decode("utf-8", errors="replace")
    else:
        text = payload

    text = html_unescape(text)

    if "&#" in text or "&lt;" in text or "&gt;" in text or "&amp;#" in text:
        text2 = html_unescape(text)
        if text2 != text:
            text = text2

    text = text.lstrip("\ufeff \t\r\n")

    root = etree.fromstring(text.encode("utf-8"))

    return root
