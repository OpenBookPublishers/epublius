#!/usr/bin/env python3

from bs4 import BeautifulSoup


class Metadata():
    def __init__(self, args):
        self.args = args

    def get_metadata(self, index, content_files):
        '''
        Return a (python) dictionary containing the information
        to add the book file
        '''

        metadata = {
            # Constants
            'toc': 'contents.xhtml',
            'copyright': 'copyright.xhtml',

            # From input arguments
            'bookpage': self.args.book,
            'booktitle': self.args.name,

            # Previus and next page
            'previous': content_files[index-1],
            'next': self.get_next(index, content_files)
        }

        return metadata

    def get_next(self, index, content_files):
        '''
        Return the filename of the following book section.

        In the special case of the last book section, take the first one.
        '''

        try:
            next = content_files[index+1]
        except IndexError:
            next = content_files[0]

        return next


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
