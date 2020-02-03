#!/usr/bin/python3

import argparse
import zipfile
import os
from bs4 import BeautifulSoup
import shutil


class Epublius:
    def __init__(self, work_dir):
        # Parse arguments
        self.argv = self.parse_args()

        self.work_dir = work_dir

    def parse_args(self, argv=None):
        '''
        Parse input arguments with argparse. 
        Return argparse object.
        '''
        
        parser = argparse.ArgumentParser(description='ePublius wrapper',
                                         add_help=False)

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

    def unzip_epub(self):
        '''
        Unzip epub file to work_dir
        '''
        
        with zipfile.ZipFile(self.argv.file, 'r') as file:
            file.extractall(self.work_dir)

    def get_contents(self):
        '''
        Parse the file ./toc.xhtml and return an ordered
        list of the files the epub is made up of.

        File names are extracted from the 'href' value of 
        each toc entry.
        '''

        toc_path = os.path.join(self.work_dir, 'OEBPS', 'toc.xhtml')
        
        with open(toc_path, 'r') as toc:
            soup = BeautifulSoup(toc, 'html.parser')
            listing = soup.find(id='toc').find_all('a')

            contents = [content['href'] for content in listing]

        return contents

    def copy_includes(self):
        '''
        Copy inclides to target directory
        '''

        shutil.copytree(os.path.join(os.getcwd(), 'includes'),
                        self.argv.output,
                        dirs_exist_ok=True)
