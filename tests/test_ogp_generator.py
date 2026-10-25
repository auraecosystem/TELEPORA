import unittest

from tools.ogp_generator import generate


BASE = {
    "title": "TELEPORA & friends",
    "type": "website",
    "url": "https://telepora.example/page?a=1&b=2",
    "image": {
        "url": "https://telepora.example/card.png",
        "width": 1200,
        "height": 630,
        "alt": 'A "preview" & image',
    },
}


class OpenGraphGeneratorTests(unittest.TestCase):
    def test_generates_required_tags_and_escapes_attributes(self):
        output = generate(BASE)
        self.assertIn('property="og:title" content="TELEPORA &amp; friends"', output)
        self.assertIn('property="og:type" content="website"', output)
        self.assertIn('property="og:url" content="https://telepora.example/page?a=1&amp;b=2"', output)
        self.assertIn('property="og:image" content="https://telepora.example/card.png"', output)
        self.assertIn('property="og:image:width" content="1200"', output)
        self.assertIn('content="A &quot;preview&quot; &amp; image"', output)

    def test_supports_multiple_images_and_optional_metadata(self):
        config = dict(BASE, image=[BASE["image"], "https://telepora.example/alternate.png"],
                      description="A project page", site_name="TELEPORA",
                      locale="en_NG", locale_alternate=["en_GB", "fr_FR"])
        output = generate(config)
        self.assertEqual(output.count('property="og:image"'), 2)
        self.assertIn('property="og:description" content="A project page"', output)
        self.assertEqual(output.count('property="og:locale:alternate"'), 2)

    def test_rejects_missing_required_fields(self):
        with self.assertRaisesRegex(ValueError, "Missing required fields"):
            generate({"title": "Only a title"})

    def test_rejects_non_http_urls(self):
        with self.assertRaisesRegex(ValueError, "absolute http\(s\) URL"):
            generate(dict(BASE, url="javascript:alert(1)"))

    def test_rejects_invalid_image_dimensions(self):
        image = dict(BASE["image"], width=0)
        with self.assertRaisesRegex(ValueError, "positive integer"):
            generate(dict(BASE, image=image))

    def test_rejects_unknown_determiner(self):
        with self.assertRaisesRegex(ValueError, "determiner must be one of"):
            generate(dict(BASE, determiner="some"))


if __name__ == "__main__":
    unittest.main()
