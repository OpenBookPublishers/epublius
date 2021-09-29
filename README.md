# ePublius
Generates a stylised HTML site from an ePub book

## Run
We encourage you to run this software with Docker.

```
docker run --rm \
  -v /path/to/local.epub:/ebook_automation/epub_file.epub \
  -v /path/to/local.json:/ebook_automation/epub_file.json \
  -v /path/to/output:/ebook_automation/output \
  -e MATHJAX=False
  openbookpublishers/epublius
```

The environment variable MATHJAX enables or disable MathJax support

Alternatively you may clone the repo, build the image using `docker build . -t some/tag` and run the command above replacing `openbookpublishers/epublius` with `some/tag`.

## Mods
Epublius has been rewritten to make it (a) modular and (b) easy to tweak.

## The *epublius* module
The *epublius* module contains:
 -  `./epublius.py` - this is where the low-level epublius functionalities live;
 -  `./metadata.py` - this produces the metadata for each book page;
 -  `./output.py` - this part takes care of merging metadata with a page template and writing the output to file.

The idea is to have separate classes for these three logic blocks to ease the transition should we want to change bits of the software in the future.

## Tweak epublius
All the action happens in the `.src/main.py` file, where `epublius` class modules are called and supplied with (almost) pedantic arguments.

The idea is to make tweaks super fast and encourage future commits.

### Parameters


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
| `-m`      | MathJax support                                                             |

## Credits
Based on software by:
(c) Nik Sultana, Open Book Publishers, September 2013 - GPLv3.
