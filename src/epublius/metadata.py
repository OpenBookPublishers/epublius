#!/usr/bin/env python3

import os
from bs4 import BeautifulSoup

class Metadata():
    def __init__(self, args, contents, work_dir):
        self.args = args
        self.contents = contents
        self.work_dir = work_dir

    def get_section_data(self, index):
        '''
        Compose a (python) dictionary containing metadata
        of the book section
        '''

        section_data = {
            # Constants
            'toc': 'contents.xhtml',
            'copyright': 'copyright.xhtml',

            # From input arguments
            'bookpage': self.args.book,
            'booktitle': self.args.name,

            # Previus and next page
            'previous': self.contents[index-1],
            'next': self.get_next(index)
        }

        return section_data

    def get_next(self, index):
        '''
        Return the filename of the following book section.

        In the special case of the last book section, take the first one.
        '''

        try:
            next = self.contents[index+1]
        except IndexError:
            next = self.contents[0]

        return next

    def get_css(self, index):
        '''
        Return a str with the CSS information of a file 
        (self.contents[index])
        '''

        file_path = os.path.join(self.work_dir, 'OEBPS',
                                 self.contents[index])

        with open(file_path, 'r') as file:
            soup = BeautifulSoup(file, 'html.parser')
            listing = soup.find_all('link')

            contents = '\n'.join([str(content) for content in listing])

        return {'book_page_css': contents}


    def get_body_text(self, index):
        '''
        Return a str with the content of the section body text
        '''

        file_path = os.path.join(self.work_dir, 'OEBPS',
                                 self.contents[index])

        with open(file_path, 'r') as file:
            soup = BeautifulSoup(file, 'html.parser')
            contents = soup.body.contents

            body_text = ''.join([str(content) for content in contents])

        return {'body_text': body_text}
