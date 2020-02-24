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

    def mathjax_support(self):
        '''
        Enable/disable MathJax support by adding or removing
        comments to the output file template.
        '''
        if self.args.mathjax == 'False':
            mathjax = {'mathjax_start': '<!--',
                       'mathjax_end': '-->'}
        else:
            mathjax = {'mathjax_start': '',
                       'mathjax_end': ''}
        return mathjax

    def get_book_url(self):
        '''
        Compose the url of the current (web) page, i.e.:
        https://www.openbookpublishers.com/htmlreader/ \
        978-1-78374-791-7/*
        '''
        return self.args.url + '*'

    def get_page_url(self):
        '''
        Compose the url of the current (web) page, i.e.:
        https://www.openbookpublishers.com/htmlreader/ \
        978-1-78374-791-7/ch1.xhtml
        '''
        url = urllib.parse.urljoin(self.args.url,
                                   self.contents[self.index])
        url_encoded = urllib.parse.quote_plus(url)

        return url_encoded


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

        file_path = os.path.join(self.work_dir,
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
