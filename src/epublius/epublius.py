#!/usr/bin/env python3

import argparse
import zipfile
import os
from bs4 import BeautifulSoup
import shutil
import pathlib


class Epublius:
    def __init__(self, work_dir):
        # Parse arguments
        self.argv = self.parse_args()

        self.work_dir = work_dir
        self.output_dir = os.path.join(self.argv.output,
                                       self.argv.isbn)

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

        parser.add_argument('-e', '--epublish',
                            help = 'Location of the ePublius script.',
                            default = '.')

        parser.add_argument('-u', '--url',
                            help = 'URL path of this book',
                            required = True)

        parser.add_argument('-t', '--template',
                            help = 'Directory containing the template ' \
                                   'files (CSS and JS)',
                            default = '.')

        parser.add_argument('-i', '--isbn',
                            help = 'Book ISBN',
                            required = True)

        parser.add_argument('-m', '--mathjax',
                            help = 'MathJax support',
                            default = False)

        return parser.parse_args(argv)

    def unzip_epub(self, prefix):
        '''
        Unzip the content of the prefix folder to work_dir.

        In standard epub file, the content of prefix would be 'OEBPS/'
        '''
        archive = zipfile.ZipFile(self.argv.file)
        out = pathlib.Path(self.work_dir)

        for archive_item in archive.namelist():
            # Skip if archive_element is a folder
            if archive_item.endswith('/'):
                continue

            # If archive_element is a file stored in the prefix folder
            if archive_item.startswith(prefix):
                # Strip the prefix from the file path
                destpath = out.joinpath(archive_item[len(prefix):])

                # Make sure destination directory exists
                os.makedirs(destpath.parent, exist_ok=True)

                with archive.open(archive_item) as source, \
                     open(destpath, 'wb') as dest:
                    shutil.copyfileobj(source, dest)

    def get_contents(self):
        '''
        Parse the file ./content.opf and return an ordered
        list of the TOC files the epub is made up of.

        File names are extracted from the 'href' value of
        each TOC entry.
        '''

        toc_path = os.path.join(self.work_dir, 'content.opf')

        # blacklist files of no interest
        blacklist = ['cover.xhtml', 'toc.xhtml']

        with open(toc_path, 'r') as toc:
            soup = BeautifulSoup(toc, 'html.parser')

            # find elements like <item media-type=application/xhtml+xml>
            listing = soup.find_all("item",
                                    {"media-type": "application/xhtml+xml"})

            # compose the list of content filenames filtering blacklist
            contents = [content['href'] for content in listing \
                        if content['href'] not in blacklist]

        return contents

    def get_cover_filepath(self):
        '''
        Parse the file ./content.opf and return a dictionary
        with the path to the cover image.
        '''

        opf_path = os.path.join(self.work_dir, 'content.opf')

        with open(opf_path, 'r') as opf_file:
            soup = BeautifulSoup(opf_file, 'html.parser')

            # find cover image entry
            cover = soup.find("item", {"properties": "cover-image"})

            if cover:
                path = cover.get('href', '')
            else:
                print('[WARNING] No cover image declared in content.opf')
                path = ''

            # compose dictionary to return
            cover_filepath = {'cover_filepath': path}

        return cover_filepath

    def copy_folders(self, parent_dir):
        '''
        Copy the subfolders recursively from parent_dir to output_directory.

        If the folder is already present in output_directory,
        simply copy the content.
        '''
        # Get a (python) dictionary of the subfolders of parent_dir
        # which looks like this: {dir_name: dir_path}
        #
        # i.e.: dirs = {'bar': '/foo/bar'}
        dirs = {dir_name: os.path.join(parent_dir, dir_name) \
                for dir_name in os.listdir(parent_dir) \
                if os.path.isdir(os.path.join(parent_dir, dir_name))}

        for dir_name, dir_path in dirs.items():
            # Copy the folder
            shutil.copytree(dir_path,
                            os.path.join(self.output_dir, dir_name),
                            dirs_exist_ok=True)

    def duplicate_contents(self):
        '''
        Duplicate content.xhtml to main.html
        '''
        shutil.copy2(os.path.join(self.output_dir, 'contents.xhtml'),
                     os.path.join(self.output_dir, 'main.html'))
