#!/usr/bin/env python3

import sys
import json
import os
import urllib.parse
import argparse
from thothlibrary import ThothClient

OUTDIR = os.getenv('OUTDIR', '../htmlreader_output')
MATHJAX = os.getenv('MATHJAX', 'False')

def query_thoth(doi_url):
    thoth = ThothClient(version="0.6.0")
    return thoth.query('workByDoi', {'doi': f'"{doi_url}"'})
    
def get_title(thoth_data):
    return thoth_data["fullTitle"]

def get_html_pub_url(thoth_data):
    for publication in thoth_data["publications"]:
        if publication['publicationType'] == 'HTML':
            url = publication['locations'][0]['fullTextUrl']
            break
    else:
        raise SystemExit('HTML publication URL not found.',
                         'This might be either because the publication is',
                         'to be entered or the associated URL is missing.')

    return url

def run():
    parser = argparse.ArgumentParser(description='Thoth wrapper')
    parser.add_argument('epub_path', help='Path to epub file')
    parser.add_argument('-d', '--doi', help='Work DOI (registered in Thoth)')
    args = parser.parse_args()
    
    doi_url = urllib.parse.urljoin('https://doi.org/', args.doi)

    thoth_data = query_thoth(doi_url)

    epublius_dir = os.getcwd()

    exe = "./main.py"
    args = [exe,
            "-b", os.getenv('BOOK_URL', doi_url),
            "-f", args.epub_path,
            "-o", OUTDIR,
            "-n", get_title(thoth_data),
            "-e", os.path.join(epublius_dir, ""),
            "-u", os.getenv('HTMLREADER_URL', get_html_pub_url(thoth_data)),
            "-t", os.path.join(epublius_dir, ""),
            "-d", args.doi,
            "-m", MATHJAX,
            "-p", os.getenv('PRIVACYPOLICY_URL', '#')]

    os.execvp(sys.executable, [exe] + args)


if __name__ == '__main__':
    run()