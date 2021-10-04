#!/usr/bin/env python3

import os
from bs4 import BeautifulSoup
import urllib.parse
import html

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

    def mathjax_support(self, mathjax_cdn):
        '''
        Enable/disable MathJax support.
        '''
        mathjax = {'mathjax': ''}

        # The reason why True is a string is that this value comes
        # from a bash generated document where boleans are not possible.
        if self.args.mathjax == 'True':
            with open(mathjax_cdn, 'r') as file:
                mathjax['mathjax'] = file.read()

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

    def get_chapter_title(self):
        '''
        Retrieve chapter title based on the text of <h1> or
        taking a guess from the file name
        (i.e. front-cover.xhtml -> "Front Cover")

        Special characters in the title are escaped before
        the ch_title varible is returned.
        '''

        h1 = self.soup.find_all('h1')

        if len(h1) == 1:
            ch_title = self.soup.h1.get_text()

        elif len(h1) > 1:
            print("[WARNING] {} has multiple h1 tags"
                  .format(self.contents[self.index]))
            ch_title = h1.pop(0).get_text()

        else:
            # Strip extension from file name
            basename = self.contents[self.index].split('.')[0]

            # Replace hypens with spaces (if any)
            title_words = basename.replace('-', ' ')

            # Create a titlecased version of title words
            ch_title = title_words.title()

        return html.escape(ch_title)

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

    def get_section_title(self):
        '''
        Return a str with the content of the title tag.

        If the title has a subtitle such as:
        'This is a Long Title: Which Includes a Subtitle'
        the method returns only the part prior the colon
        '''

        full_title = self.get_chapter_title()
        shortened_title = full_title.split(':')[0]

        return {'section_title': shortened_title}
