import json
import re
import urllib.request
from datetime import datetime, timezone
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from xml.etree import ElementTree as ET

SOURCE_URL = "https://reefnafood.com/products.json?limit=250"
OUTPUT = Path("reefna-meta-product-feed.xml")
BASE_URL = "https://reefnafood.com"
CURRENCY = "EGP"
G_NS = "http://base.google.com/ns/1.0"
ET.register_namespace("g", G_NS)


class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []

    def handle_data(self, data):
        value = data.strip()
        if value:
            self.parts.append(value)


def clean_html(value):
    parser = TextExtractor()
    parser.feed(value or "")
    parser.close()
    return re.sub(r"\s+", " ", unescape(" ".join(parser.parts))).strip()


def add(parent, name, value, namespace=None):
    tag = f"{{{namespace}}}{name}" if namespace else name
    node = ET.SubElement(parent, tag)
    node.text = str(value)


def money(value):
    return f"{float(value):.2f} {CURRENCY}"


def image_for(product, variant):
    featured = variant.get("featured_image") or {}
    if featured.get("src"):
        return featured["src"]
    images = product.get("images") or []
    return images[0].get("src", "") if images else ""


request = urllib.request.Request(SOURCE_URL, headers={"User-Agent": "ReefnaMetaFeed/1.0"})
with urllib.request.urlopen(request, timeout=60) as response:
    products = json.load(response).get("products", [])

rss = ET.Element("rss", {"version": "2.0"})
channel = ET.SubElement(rss, "channel")
add(channel, "title", "Reefna Food – Meta Product Feed")
add(channel, "link", BASE_URL)
add(channel, "description", "Reefna Food product catalog for Meta/Facebook and Instagram")
add(channel, "lastBuildDate", datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000"))

count = 0
for product in products:
    product_id = str(product["id"])
    product_title = (product.get("title") or "").strip()
    description = clean_html(product.get("body_html")) or product_title
    brand = (product.get("vendor") or "Reefna Food").strip()
    product_type = (product.get("product_type") or "").strip()
    images = [image.get("src", "") for image in product.get("images", []) if image.get("src")]

    for variant in product.get("variants", []):
        variant_id = str(variant["id"])
        variant_title = (variant.get("title") or "").strip()
        title = product_title if not variant_title or variant_title.lower() == "default title" else f"{product_title} – {variant_title}"
        item = ET.SubElement(channel, "item")
        add(item, "id", f"shopify_EG_{product_id}_{variant_id}", G_NS)
        add(item, "item_group_id", f"shopify_EG_{product_id}", G_NS)
        add(item, "title", title, G_NS)
        add(item, "description", description, G_NS)
        add(item, "availability", "in stock" if variant.get("available") else "out of stock", G_NS)
        add(item, "condition", "new", G_NS)
        current = variant.get("price") or "0"
        compare_at = variant.get("compare_at_price")
        if compare_at and float(compare_at) > float(current):
            add(item, "price", money(compare_at), G_NS)
            add(item, "sale_price", money(current), G_NS)
        else:
            add(item, "price", money(current), G_NS)
        add(item, "link", f"{BASE_URL}/products/{product['handle']}?variant={variant_id}", G_NS)
        primary_image = image_for(product, variant)
        add(item, "image_link", primary_image, G_NS)
        for image_url in images:
            if image_url != primary_image:
                add(item, "additional_image_link", image_url, G_NS)
        add(item, "brand", brand, G_NS)
        sku = (variant.get("sku") or "").strip()
        if sku:
            add(item, "mpn", sku, G_NS)
        if product_type:
            add(item, "product_type", product_type, G_NS)
        count += 1

ET.indent(rss, space="  ")
ET.ElementTree(rss).write(OUTPUT, encoding="utf-8", xml_declaration=True)
print(f"Generated {count} catalog items from {len(products)} products")
