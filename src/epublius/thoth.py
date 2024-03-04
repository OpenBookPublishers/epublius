#!/usr/bin/env python3

from os import getenv
from thothlibrary import ThothClient
import urllib.parse


class Thoth:
    '''
    Module to handle Thoth interactions
    '''

    def __init__(self):
        self.client = ThothClient()
        self.logged_in = self.login()

    def login(self):
        username = getenv('THOTH_EMAIL')
        password = getenv('THOTH_PWD')
        if username is None:
            print('[WARNING] No Thoth username provided '
                '(THOTH_EMAIL environment variable not set)')
            return False
        if password is None:
            print('[WARNING] No Thoth password provided '
                '(THOTH_PWD environment variable not set)')
            return False
        try:
            self.client.login(username, password)
            return True
        except:
            return False

    def write_urls(self, metadata, book_doi):
        '''
        Write chapter Landing Page and Full Text URLs
        to Thoth in standard OBP format
        '''
        chapter_doi_full = metadata.get_chapter_doi()

        # Skip chapters that don't have a DOI
        if chapter_doi_full is not None:
            work_id = self.client.work_by_doi(chapter_doi_full).workId
            chapter_doi = chapter_doi_full.split('doi.org/')[-1].lower()
            landing_page_root = (
                'https://www.openbookpublishers.com/books/'
                '{book_doi}/chapters/{chapter_doi}')

            publication = {"workId":          work_id,
                           "publicationType": "HTML",
                           "isbn":            None,
                           "widthMm":         None,
                           "widthIn":         None,
                           "heightMm":        None,
                           "heightIn":        None,
                           "depthMm":         None,
                           "depthIn":         None,
                           "weightG":         None,
                           "weightOz":        None}
            publication_id = self.client.create_publication(publication)

            location = {"publicationId":    publication_id,
                        "landingPage":      landing_page_root.format(
                            book_doi=book_doi, chapter_doi=chapter_doi),
                        "fullTextUrl":      urllib.parse.unquote_plus(
                            metadata.get_page_url()),
                        "locationPlatform": "PUBLISHER_WEBSITE",
                        "canonical":        "true"}
            self.client.create_location(location)

            print('{}: URLs written to Thoth'.format(
                metadata.contents[metadata.index]))
