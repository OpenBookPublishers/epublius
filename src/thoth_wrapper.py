#!/usr/bin/env python3

import sys
import os
import urllib.parse
import argparse
from thothlibrary import ThothClient

OUTDIR = os.getenv('OUTDIR', '../htmlreader_output')
MATHJAX = os.getenv('MATHJAX', 'False')

def query_thoth(doi_url):
    thoth = ThothClient()
    return thoth.work_by_doi(doi=doi_url)

def get_title(work):
    titles = getattr(work, "titles", []) or []

    for title in titles:
        if getattr(title, "canonical", False):
            return getattr(title, "fullTitle", getattr(title, "title", None))

    if titles:
        title = titles[0]
        return getattr(title, "fullTitle", getattr(title, "title", None))

    full_title = getattr(work, "fullTitle", None)
    if full_title is not None:
        return full_title

    raise ValueError('Title data not found in Thoth.',
                     'Please add it and re-run the process.')

def get_html_pub_url(work):
    for publication in getattr(work, "publications", []):
        if getattr(publication, 'publicationType', None) == 'HTML':
            locations = getattr(publication, 'locations', [])
            break
    else:
        raise ValueError('HTML edition data not found in Thoth.',
                         'Please add it and re-run the process.')

    try:
        url = locations[0].fullTextUrl
    except (AttributeError, IndexError):
        raise IndexError('HTML edition defined in Thoth but '
                         'location URL not specified. Please, '
                         'add it and re-run the process.')

    # Add trailing slash if not present - needed for correct URL concatenation
    if url.endswith('/'):
        return url
    else:
        return url + '/'

def run():
    parser = argparse.ArgumentParser(description='Thoth wrapper')
    parser.add_argument('epub_path', help='Path to epub file')
    parser.add_argument('-d', '--doi', help='Work DOI (registered in Thoth)', required=True)
    args = parser.parse_args()

    doi_url = urllib.parse.urljoin('https://doi.org/', args.doi)

    work = query_thoth(doi_url)

    epublius_dir = os.getcwd()

    exe = "./main.py"
    args = [exe,
            "-b", os.getenv('BOOK_URL', doi_url),
            "-f", args.epub_path,
            "-o", OUTDIR,
            "-n", get_title(work),
            "-e", os.path.join(epublius_dir, ""),
            "-u", os.getenv('HTMLREADER_URL', get_html_pub_url(work)),
            "-t", os.path.join(epublius_dir, ""),
            "-d", args.doi,
            "-m", MATHJAX,
            "-p", os.getenv('PRIVACYPOLICY_URL', '#'),
            "-w", 'True']

    os.execvp(sys.executable, [exe] + args)


if __name__ == '__main__':
    run()
