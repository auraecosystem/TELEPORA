# Open Graph implementation notes

## What the generator does

`tools/ogp_generator.py` turns a JSON object into HTML Open Graph meta tags. It uses only the Python standard library and can write to stdout or a specified output file.

Required configuration keys:

- `title`: non-empty page/object title.
- `type`: non-empty Open Graph object type, such as `website` or `article`.
- `url`: canonical absolute `http://` or `https://` URL.
- `image`: an absolute HTTP(S) URL, or a non-empty list of image URL strings / objects.

Image objects support `url`, `secure_url`, `type`, positive integer `width` and `height`, and descriptive `alt`. Optional top-level fields are `description`, `site_name`, `locale`, `determiner`, `audio`, `video`, and `locale_alternate` (a list). The generator HTML-escapes attribute values and rejects malformed URLs, missing required fields, invalid dimensions, and invalid determiner values.

Example:

```sh
python tools/ogp_generator.py examples/ogp-config.example.json
python tools/ogp_generator.py examples/ogp-config.example.json --output generated/ogp-tags.html
```

The output is a fragment, not a complete HTML page. Insert it into the document's `<head>`. Keep the first value of any repeated property as the preferred value, consistent with the OGP array behavior documented in `Implementation/OGP/README.md`.

## Tests

Run `python -m unittest discover -s tests -v`. Tests cover required metadata, HTML escaping, multiple images, optional tags, URL validation, and image dimension validation. The implementation has no external runtime dependencies.

## Audit notes from the repository snapshot

- `Implementation/OGP/README.md` contains the main human-readable protocol description and describes the four required properties: `og:title`, `og:type`, `og:image`, and `og:url`.
- `ogp.me/ns/html.RDF` contains Markdown-like documentation in a fenced block rather than valid RDF/RDFa/Turtle serialization. Do not advertise it as a machine-readable RDF schema until it is replaced with a valid schema and checked with an RDF parser.
- `ogp.me/ns/index.yaml` and `www/site/html.yaml` were effectively empty in the inspected snapshot. No real production page URL or verified social preview image was present in that snapshot, so this change does not invent live production metadata.
- `www/site/ns/assets/js/button.js` begins with `jacascript:void(0)<button>`, which does not look like a valid JavaScript module. It is outside this metadata-generator change and should be investigated separately before being repaired, because the intended UI behavior is unknown.

## Before production integration

1. Confirm the public canonical site URL and the exact title, description, locale, and site name.
2. Create or identify a real social card image that is publicly reachable over HTTPS. Set accurate `og:image:alt`, dimensions, and MIME type.
3. Generate the metadata and insert it into the actual HTML template or static page head. This repository snapshot did not expose a working page template/build pipeline to integrate automatically.
4. Check rendered HTML in the browser and verify the image is fetchable without authentication or redirects that social crawlers cannot follow.
5. Test a deployed URL with the intended social platform's current preview/debugging tool and check canonical URL, image crop, title, and description.
6. If machine-readable schema files are required, restore the intended RDF/Turtle schema separately and validate it with a compatible parser.
