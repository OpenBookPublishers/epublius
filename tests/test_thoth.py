import io
import os
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_DIR))

from epublius import thoth as thoth_module
import thoth_wrapper


class TestThothWrapper(unittest.TestCase):
    def test_get_title_prefers_canonical_title(self):
        work = SimpleNamespace(
            titles=[
                SimpleNamespace(
                    canonical=False,
                    fullTitle="Fallback Title",
                    title="Fallback Title",
                ),
                SimpleNamespace(
                    canonical=True,
                    fullTitle="Canonical Title",
                    title="Canonical Title",
                ),
            ]
        )

        self.assertEqual(thoth_wrapper.get_title(work), "Canonical Title")

    def test_get_html_pub_url_appends_trailing_slash(self):
        work = SimpleNamespace(
            publications=[
                SimpleNamespace(publicationType="PDF", locations=[]),
                SimpleNamespace(
                    publicationType="HTML",
                    locations=[SimpleNamespace(fullTextUrl="https://example.com/book")],
                ),
            ]
        )

        self.assertEqual(
            thoth_wrapper.get_html_pub_url(work),
            "https://example.com/book/",
        )

    def test_get_html_pub_url_raises_when_location_missing(self):
        work = SimpleNamespace(
            publications=[SimpleNamespace(publicationType="HTML", locations=[])]
        )

        with self.assertRaises(IndexError):
            thoth_wrapper.get_html_pub_url(work)


class TestThothAuth(unittest.TestCase):
    def test_login_warns_when_pat_missing(self):
        with patch.object(thoth_module, "ThothClient") as mock_client:
            with patch.dict(os.environ, {}, clear=True):
                with patch("sys.stdout", new_callable=io.StringIO) as stdout:
                    thoth = thoth_module.Thoth()

        self.assertFalse(thoth.logged_in)
        self.assertIn("THOTH_PAT environment variable not set", stdout.getvalue())
        mock_client.return_value.set_token.assert_not_called()


if __name__ == "__main__":
    unittest.main()
