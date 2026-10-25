# TELEPORA

TELEPORA contains the Open Graph Protocol reference in [`Implementation/OGP/README.md`](Implementation/OGP/README.md) and a small, dependency-free Python tool for generating Open Graph `<meta>` tags from JSON.

## Generate metadata

Python 3.10 or newer is recommended. No third-party packages are required.

```sh
python tools/ogp_generator.py examples/ogp-config.example.json
python tools/ogp_generator.py examples/ogp-config.example.json --output /tmp/ogp-tags.html
```

The example uses reserved `example.com` URLs and is illustrative only. Replace the title, canonical URL, image URL, image description, and other values with real values before publishing. Add the generated tags inside the page's HTML `<head>`.

## Validate

```sh
python -m unittest discover -s tests -v
```

See [`docs/OGP-IMPLEMENTATION.md`](docs/OGP-IMPLEMENTATION.md) for the supported config, validation rules, audit notes, and integration checklist.
