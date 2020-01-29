#!/usr/bin/python2.7

import argparse


class Epublius:
    def __init__(self):
        # Parse arguments
        self.argv = self.parse_args()

    def parse_args(self, argv=None):
        '''
        Parse input arguments with argparse. 
        Return argparse object.
        '''
        
        parser = argparse.ArgumentParser(description='ePublius wrapper',
                                         add_help=False)

        parser.add_argument('-p', '--prefix',
                            help = 'file containing prefix',
                            required = True)

        parser.add_argument('-s', '--suffix',
                            help = 'file containing suffix',
                            required = True)

        parser.add_argument('--help',
                            action='help',
                            default=argparse.SUPPRESS,
                            help=argparse._('show this help message and exit'))

        parser.add_argument('-h', '--header',
                            help = 'file containing HTML to inject into header',
                            required = True)

        parser.add_argument('-b', '--book',
                            help = 'URL of book\'s page',
                            required = True)

        parser.add_argument('-f', '--file',
                            help = 'ePub file (or contents, if -z is used)',
                            required = True)

        parser.add_argument('-o', '--output',
                            help = 'Target directory',
                            required = True)

        parser.add_argument('-n', '--name',
                            help = 'Book name',
                            required = True)

        parser.add_argument('-r', '--resample',
                            help = 'Resample image (as percentage; ' \
                            'default is 50, no resampling is 100).',
                            default = None,
                            type = int)

        parser.add_argument('-e', '--epublish',
                            help = 'Location of the ePublius script.',
                            default = '.')

        parser.add_argument('-u', '--url',
                            help = 'URL path of this book',
                            required = True)

        parser.add_argument('-a', '--donation',
                            help = 'Donation link',
                            default = None)

        parser.add_argument('-t', '--template',
                            help = 'Directory containing the template ' \
                                   'files (CSS and JS)',
                            default = '.')

        return parser.parse_args(argv)
