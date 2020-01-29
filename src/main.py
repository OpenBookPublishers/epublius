#!/usr/bin/python2

import random
import time
import os
import sys
import glob
import subprocess
import commands
import shutil
import re
import string
import argparse
import epub_extract
from zipfile import ZipFile
import tempfile
from bs4 import BeautifulSoup
from epublius import epublius


def fake_command(s):
  args = s.split(" ")
  output = subprocess.check_output(args)
  return 0, output

def create_tmpdir():
  tmpdir = tempfile.mkdtemp(prefix='epublius_')

  return tmpdir

def main():

  core = epublius.Epublius()
  
  args = core.argv
  process_epub(args)

def process_epub(args):
  ## TODO We should use a dictionary instead of so many variables.
  ## Keeping the original notation as legacy code.
  prefix_file = args.prefix
  suffix_file = args.suffix
  headeradd_file = args.header
  book_page = args.book
  epub_file = args.file
  target_directory = args.output
  book_title = args.name
  resize_percent = args.resample
  ePublius_path = args.epublish
  url_prefix = args.url
  donation_link = args.donation
  template_dir = args.template


  tmpdir = create_tmpdir()

  # Unzip epub to tmpdir
  with ZipFile(epub_file, 'r') as zip_file:
    zip_file.extractall(tmpdir)

  # path where xhtml and folders are expected
  path = os.path.join(tmpdir, 'OEBPS')

  def parse_toc(toc_path):
    '''
    Parse the file ./toc.xhtml and return an ordered
    list of the files the epub is made up of.

    File names are extracted from the 'href' value of 
    each toc entry.
    '''
    
    with open(toc_path, 'r') as toc:
      soup = BeautifulSoup(toc, 'html.parser')
      listing = soup.find(id='toc').find_all('a')

      contents = [content['href'].encode('utf-8') \
                  for content in listing]

      return contents

  # Get a list of the ebook content files
  content_files = parse_toc(os.path.join(path, 'toc.xhtml'))

  colophon_files = []
  toc_file = 'contents.xhtml'
  title_file = 'title.xhtml'
  copyright_file = 'copyright.xhtml'


  target_directory = target_directory + "/" #FIXME check for this
  os.makedirs(target_directory)


  # Duplicate contents.xhtml to main.html
  landing_file = "main.html"
  shutil.copy2(os.path.join(path, toc_file),
               os.path.join(path, landing_file))
               
  if donation_link is None:
    donation_link = ""

  if resize_percent is None:
    resize_percent = 50

  copyright_arg = copyright_file
  url_arg = url_prefix + donation_link

  index_file = "" # ??

  epub_extract.extract_all(
    prefix_file,
    suffix_file,
    headeradd_file,
    colophon_files,
    path,
    toc_file,
    book_title,
    url_arg,
    target_directory,
    index_file,
    landing_file,
    book_page,
    copyright_arg,
    donation_link,
    resize_percent
  )

  # We recopy the file, since when we earlier copied the file it had
  # not yet been processed by epublius, but now it has.
  #
  # TODO PLEASE GET RID OF THIS REPETITION
  shutil.copy2(os.path.join(path, toc_file),
               os.path.join(path, landing_file))


  shutil.copy2(os.path.join(template_dir, 'html-style.css'),
               os.path.join(target_directory, 'css'))

  shutil.copytree(os.path.join(template_dir, 'JS'),
                  os.path.join(target_directory, 'JS'))

  shutil.copytree(os.path.join(template_dir, 'logo'),
                  os.path.join(target_directory, 'logo'))

  shutil.rmtree(tmpdir)

  # ZIP OUTPUT FOLDER
  # if target_directory looks like:
  # ../htmlreader_output/978-1-78374-863-1/

  # -> base_dir = '978-1-78374-863-1'
  base_dir = target_directory.split('/')[-2]

  # -> root_dir = '../htmlreader_output'
  root_dir = '/'.join([target_directory.split('/')[0],
                       target_directory.split('/')[1]])

#  shutil.make_archive(base_dir=base_dir,
#                      root_dir=root_dir,
#                      format='zip',
#                      base_name=target_directory)

#  shutil.rmtree(target_directory)

if __name__ == '__main__':
  main()
