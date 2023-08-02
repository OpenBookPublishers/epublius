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
        Compose the url of the current (web) page, e.g.:
        https://books.openbookpublishers.com/10.11647/ \
        obp.9999/*
        '''
        return self.args.url + '*'

    def get_page_url(self):
        '''
        Compose the url of the current (web) page, e.g.:
        https://books.openbookpublishers.com/10.11647/ \
        obp.9999/ch1.xhtml
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
            soup = BeautifulSoup(file, features='xml')

        return soup

    def get_chapter_title(self):
        '''
        Retrieve chapter title based on the text of <title> or
        taking a guess from the file name
        (i.e. front-cover.xhtml -> "Front Cover")

        Special characters in the title are escaped before
        the ch_title varible is returned.
        '''

        title_node = self.soup.title

        if (title_node is not None) and \
           (title_node.string is not None):
            ch_title = title_node.string
        else:
            basename = os.path.splitext(self.contents[self.index])[0]
            title_words = basename.replace('-', ' ')
            ch_title = title_words.title()

        return html.escape(ch_title)

    def get_chapter_doi(self):
        '''
        Retrieve chapter DOI based on the text of <p class=doi>
        (this contains both copyright statement and DOI link)
        '''
        # Not all chapters will have DOIs
        doi = None

        doi_node = self.soup.find('p', class_='doi')

        if (doi_node is not None):
            doi_link = doi_node.a
            if (doi_link is not None) and (doi_link.string is not None):
                doi = doi_link.string

        return doi

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

    def get_privacy_policy_url(self):
        '''
        Return a str with the privacy policy URL.
        '''
        return {'privacy_policy_url': self.args.privacy_policy}
