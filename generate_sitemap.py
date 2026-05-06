from __future__ import annotations

from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "sitemap.xml"
SITE_URL = "https://hridyafarm.com"

URLSET_ATTRS = {"xmlns": "http://www.sitemaps.org/schemas/sitemap/0.9"}


class CanonicalParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.canonical: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "link":
            return
        attr_map = dict(attrs)
        if attr_map.get("rel") == "canonical" and attr_map.get("href"):
            self.canonical = attr_map["href"]


def discover_pages() -> Iterable[Path]:
    for path in sorted(ROOT.glob("*.html")):
        if path.name.startswith("."):
            continue
        yield path


def extract_canonical(path: Path) -> str:
    parser = CanonicalParser()
    parser.feed(path.read_text())
    if parser.canonical:
        return parser.canonical.strip()
    suffix = "" if path.name == "index.html" else f"/{path.name}"
    return f"{SITE_URL}{suffix}"


def infer_priority(path: Path) -> str:
    if path.name == "index.html":
        return "1.0"
    if path.name == "blog.html":
        return "0.9"
    return "0.8"


def infer_changefreq(path: Path) -> str:
    if path.name == "index.html":
        return "daily"
    if path.name == "blog.html":
        return "daily"
    return "weekly"


def iso_lastmod(path: Path) -> str:
    ts = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
    return ts.date().isoformat()


def build_sitemap() -> ET.ElementTree:
    urlset = ET.Element("urlset", URLSET_ATTRS)
    for path in discover_pages():
        url = ET.SubElement(urlset, "url")
        ET.SubElement(url, "loc").text = extract_canonical(path)
        ET.SubElement(url, "lastmod").text = iso_lastmod(path)
        ET.SubElement(url, "changefreq").text = infer_changefreq(path)
        ET.SubElement(url, "priority").text = infer_priority(path)
    return ET.ElementTree(urlset)


def indent(elem: ET.Element, level: int = 0) -> None:
    indentation = "\n" + level * "  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = indentation + "  "
        for child in elem:
            indent(child, level + 1)
        if not child.tail or not child.tail.strip():
            child.tail = indentation
    elif level and (not elem.tail or not elem.tail.strip()):
        elem.tail = indentation


def main() -> None:
    tree = build_sitemap()
    indent(tree.getroot())
    tree.write(OUTPUT, encoding="utf-8", xml_declaration=True)
    print(f"Updated {OUTPUT}")


if __name__ == "__main__":
    main()
