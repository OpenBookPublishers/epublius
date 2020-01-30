#!/usr/bin/python2.7


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
