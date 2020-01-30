#!/usr/bin/env python3

from bs4 import BeautifulSoup


class Parse_tools():
    def __init__(self):
        pass

    def parse_toc(self, toc_path):
        '''
        Parse the file ./toc.xhtml and return an ordered
        list of the files the epub is made up of.

        File names are extracted from the 'href' value of 
        each toc entry.
        '''
        with open(toc_path, 'r') as toc:
            soup = BeautifulSoup(toc, 'html.parser')
            listing = soup.find(id='toc').find_all('a')

            contents = [content['href'].encode('utf-8') \
                        for content in listing]

        return contents
