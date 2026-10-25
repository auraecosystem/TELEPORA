#!/usr/bin/env python3
"""Generate validated Open Graph HTML metadata from a JSON document.

Usage: python tools/ogp_generator.py examples/ogp-config.example.json
"""
from __future__ import annotations

import argparse
import json
import sys
from html import escape
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

REQUIRED = ("title", "type", "image", "url")
OPTIONAL = ("description", "site_name", "locale", "determiner", "audio", "video")


def _text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    return value.strip()


def _url(value: Any, field: str) -> str:
    value = _text(value, field)
    parsed = urlparse(value)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise ValueError(f"{field} must be an absolute http(s) URL")
    return value


def _tag(prop: str, value: Any) -> str:
    return f'<meta property="{escape(prop, quote=True)}" content="{escape(str(value), quote=True)}" />'


def generate(config: dict[str, Any]) -> str:
    """Validate config and return a ready-to-paste sequence of meta tags."""
    if not isinstance(config, dict):
        raise ValueError("The JSON root must be an object")
    missing = [key for key in REQUIRED if key not in config]
    if missing:
        raise ValueError("Missing required fields: " + ", ".join(missing))

    title = _text(config["title"], "title")
    og_type = _text(config["type"], "type")
    canonical_url = _url(config["url"], "url")
    images = config["image"]
    if isinstance(images, str):
        images = [{"url": images}]
    if not isinstance(images, list) or not images:
        raise ValueError("image must be a URL string or a non-empty list of image objects")

    lines = [
        _tag("og:title", title),
        _tag("og:type", og_type),
        _tag("og:url", canonical_url),
    ]
    for index, image in enumerate(images):
        if isinstance(image, str):
            image = {"url": image}
        if not isinstance(image, dict) or "url" not in image:
            raise ValueError(f"image[{index}] must be a URL string or object containing url")
        image_url = _url(image["url"], f"image[{index}].url")
        lines.append(_tag("og:image", image_url))
        for field, suffix in (("secure_url", "secure_url"), ("type", "type"), ("width", "width"), ("height", "height"), ("alt", "alt")):
            if field in image and image[field] is not None:
                value = image[field]
                if field in ("width", "height"):
                    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                        raise ValueError(f"image[{index}].{field} must be a positive integer")
                elif field == "secure_url":
                    value = _url(value, f"image[{index}].secure_url")
                else:
                    value = _text(value, f"image[{index}].{field}")
                lines.append(_tag(f"og:image:{suffix}", value))

    for key in OPTIONAL:
        if key not in config or config[key] is None:
            continue
        raw_value = config[key]
        value = "" if key == "determiner" and raw_value == "" else _text(raw_value, key)
        if key in ("audio", "video"):
            value = _url(value, key)
        if key == "determiner" and value not in ("", "a", "an", "the", "auto"):
            raise ValueError('determiner must be one of: "", a, an, the, auto')
        lines.append(_tag(f"og:{key}", value))

    alternate_locales = config.get("locale_alternate", [])
    if not isinstance(alternate_locales, list):
        raise ValueError("locale_alternate must be a list of locale strings")
    for locale in alternate_locales:
        lines.append(_tag("og:locale:alternate", _text(locale, "locale_alternate item")))

    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", type=Path, help="Path to a JSON metadata config")
    parser.add_argument("-o", "--output", type=Path, help="Write output to a file instead of stdout")
    args = parser.parse_args(argv)
    try:
        config = json.loads(args.config.read_text(encoding="utf-8"))
        result = generate(config)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(result, encoding="utf-8")
        else:
            sys.stdout.write(result)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"ogp-generator: error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
