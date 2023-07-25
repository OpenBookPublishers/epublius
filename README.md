# epublius

A tool to generate a standalone website from an EPUB.

## Usage

The entry point is `.src/main.py`, which can be called with the following arguments:

| Parameter | Description                                                               |
|-----------|---------------------------------------------------------------------------|
| `-b`      | URL of book's page                                                        |
| `-t`      | TOC file                                                                  |
| `-f`      | Frontpage file                                                            |
| `-d`      | Directory prefix (of content, not prefix/suffix)                          |
| `-o`      | Target directory                                                          |
| `-h`      | File containing HTML to inject into header                                |
| `-n`      | Title name                                                                |
| `-c`      | A colophon file (e.g., the license). There may be  multiple -c parameters |
| `-r`      | How much to resize the images (as percentage; default is 50).             |
| `-u`      | URL path of this book                                                     |
| `-k`      | Copyright file                                                            |
| `-a`      | Donation link                                                             |
| `-m`      | MathJax support                                                           |
| `-p`      | Privacy policy URL                                                        |
| `-w`      | Write chapter URLs to Thoth (True/False)                                  |


## Thoth Wrapper (Optional)

### Installation

Clone the repo and build the image with $ `docker build . -t openbookpublishers/epublius`.

### Usage

```bash
docker run --rm \
           -v /path/to/local.epub:/ebook_automation/epub_file.epub \
           -v /path/to/output:/ebook_automation/output \
           -e MATHJAX=False \
           -e PRIVACYPOLICY_URL=https://example.org \
           -e THOTH_EMAIL=email@example.com \
           -e THOTH_PWD=password \
           openbookpublishers/epublius \
	   thoth_wrapper.py /ebook_automation/epub_file.epub \
                            --doi 10.11647/obp.0275
```

The environment variable MATHJAX enables or disable MathJax support
The environment variables THOTH_EMAIL and THOTH_PWD allow use of the `--write-urls` option by providing Thoth credentials

## Contributing

Pull requests are welcome.

## License

[GPLv3](https://www.gnu.org/licenses/gpl-3.0.en.html)
