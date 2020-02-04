#!/usr/bin/env python3

import os
from bs4 import BeautifulSoup
import urllib.parse

class Metadata():
    def __init__(self, args, work_dir, index, contents):
        self.args = args
        self.work_dir = work_dir
        self.contents = contents
        self.index = index

        self.soup = self.get_file_soup()
        
    def get_section_data(self):
        '''
        Compose a (python) dictionary containing metadata
        of the book section
        '''

        # Truncate book title to the first ':' occurrence
        book_title = self.args.name.split(':')[0]

        section_data = {
            # Constants
            'toc': 'contents.xhtml',
            'copyright': 'copyright.xhtml',

            # From input arguments
            'book_web_page': self.args.book,
            'book_title': book_title,

            # Page and book URLs
            'this_page_url': self.get_page_url(),
            'this_book_url': self.get_book_url(),
            
            # Previus and next page
            'previous': self.contents[self.index - 1],
            'next': self.get_next()
        }

        return section_data

    def get_reader_url(self, page):
        '''
        Compose a generic url of the current epublius instance, 
        to be specialized by the methods 

        self.get_book_url and self.get_page_url

        the url returned looks like thisi.e.:
        https://www.openbookpublishers.com/htmlreader/ \
        978-1-78374-791-7/ch1.xhtml

        urllib.urljoin() can't join multiple folders/paths,
        so the task is performed with a simple join()

        The url is finally encoded to allow google translator
        to parse it.
        '''

        url_prefix = 'https://www.openbookpublishers.com/htmlreader'
        isbn = self.args.output.split('/')[-1]
        
        url =  '/'.join([url_prefix, isbn, page])
        encoded_url = urllib.parse.quote_plus(url)

        return encoded_url

    def get_book_url(self):
        '''
        Compose the url of the current (web) page, i.e.:
        https://www.openbookpublishers.com/htmlreader/ \
        978-1-78374-791-7/*
        '''
        return self.get_reader_url('*')

    def get_page_url(self):
        '''
        Compose the url of the current (web) page, i.e.:
        https://www.openbookpublishers.com/htmlreader/ \
        978-1-78374-791-7/ch1.xhtml
        '''
        return self.get_reader_url(self.contents[self.index])

    def get_next(self):
        '''
        Return the filename of the following book section.

        In the special case of the last book section, take the first one.
        '''

        try:
            next = self.contents[self.index + 1]
        except IndexError:
            next = self.contents[0]

        return next

    def get_file_soup(self):
        '''
        make a beautiful soup object of the content file
        '''

        file_path = os.path.join(self.work_dir, 'OEBPS',
                                 self.contents[self.index])

        with open(file_path, 'r') as file:
            soup = BeautifulSoup(file, 'html.parser')

        return soup
        
    def get_css(self):
        '''
        Return a str with the CSS information of a file 
        (self.contents[index])
        '''
        listing = self.soup.find_all('link')

        contents = '\n'.join([str(content) for content in listing])

        return {'book_page_css': contents}

    def get_body_text(self):
        '''
        Return a str with the content of the section body text
        '''
        contents = self.soup.body.contents

        body_text = ''.join([str(content) for content in contents])

        return {'body_text': body_text}

    def get_breadcrumbs(self):
        '''
        Return a str with the content of the title tag.

        If the title has a subtitle such as:
        'This is a Long Title: Which Includes a Subtitle'
        the method returns only the part prior the colon
        '''

        title = self.soup.find('title').text
        breadcrumbs = title.split(':')[0]

        return {'breadcrumbs': breadcrumbs}
