#!/usr/bin/env python3

import sys
import json
import os
import requests
import urllib.parse

OUTDIR = os.getenv('OUTDIR', '../htmlreader_output')
MATHJAX = os.getenv('MATHJAX', 'False')

def query_thoth(book_doi):
    url = 'https://api.thoth.pub/graphql'
    query = {"query": "{ workByDoi (doi: \"%s\") { \
                           fullTitle \
                           publications { \
                              publicationType \
                              locations(locationPlatform: OTHER){ \
                                 fullTextUrl \
                                 } \
                              } \
                           } \
                        }" % book_doi}

    # handle connection issues
    try:
        r = requests.post(url, json=query)
        r.raise_for_status()
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)

    return json.loads(r.text)

def get_title(thoth_data):
    # handle bad responses
    try:
        print(thoth_data)
        title = thoth_data["data"]["workByDoi"]["fullTitle"]
    except TypeError as err:
        print('The graphql query did not produce a valid response.',
              'thoth_data["data"]["workByDoi"]["fullTitle"] not found.',
              'It is possible that a bad DOI was supplied.')
        raise SystemExit(err)

    return title

def get_html_pub_url(thoth_data):
    try:
        publications = thoth_data["data"]["workByDoi"]["publications"]
    except TypeError as err:
        print('The graphql query did not produce a valid response.',
              'thoth_data["data"]["workByDoi"]["publications"] not found.')
        raise SystemExit(err)

    for publication in publications:
        if publication['publicationType'] == 'HTML' \
           and publication['locations'][0]['fullTextUrl']:
            url = publication['locations'][0]['fullTextUrl']
            break
    else:
        raise SystemExit('HTML publication URL not found.',
                         'This might be either because the publication is',
                         'to be entered or the associated URL is missing.')

    return url

def run():
    _, metadata_path, epub_path = sys.argv
    with open(metadata_path) as f:
        metadata = json.load(f)

    doi = str(metadata['doi'])
    book_doi = urllib.parse.urljoin('https://doi.org/', doi)

    thoth_data = query_thoth(book_doi)

    epublius_dir = os.getcwd()

    exe = "./main.py"
    args = [exe,
            "-b", os.getenv('BOOK_URL', book_doi),
            "-f", epub_path,
            "-o", OUTDIR,
            "-n", get_title(thoth_data),
            "-e", os.path.join(epublius_dir, ""),
            "-u", os.getenv('HTMLREADER_URL', get_html_pub_url(thoth_data)),
            "-t", os.path.join(epublius_dir, ""),
            "-d", metadata['doi'],
            "-m", MATHJAX,
            "-p", os.getenv('PRIVACYPOLICY_URL', '#')]

    os.execvp(sys.executable, [exe] + args)


if __name__ == '__main__':
    run()
