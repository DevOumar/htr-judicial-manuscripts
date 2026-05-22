
from lxml import etree

root = etree.Element("PcGts")

page = etree.SubElement(root, "Page")
page.set("imageFilename", "sample_1.png")

tree = etree.ElementTree(root)

tree.write(
    "page_xml/sample.xml",
    pretty_print=True,
    xml_declaration=True,
    encoding="utf-8"
)

print("PAGE XML generated.")
