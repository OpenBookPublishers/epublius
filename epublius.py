#!/usr/bin/python2
#
# ePublius
# Given the contents of an ePub, and indications of specific files of interest
# (e.g. the filenames of the cover and contents files), and certain templates,
# it generates a web-friendly version of the ePub's contents.
#
# (c) Nik Sultana, Open Book Publishers, September 2013
# Use of this software is governed by the terms of the GPLv3 -- see LICENSE.
#
# Example usage:
#    ./epublius.py -p prefix -s suffix -f 02_title.html -t 06_toc.html \
#        -b https://www.openbookpublishers.com/product/97 -d ../epub/OEBPS/ \
#        -o ../epub/new/ -h header_add
#
# What it does:
# 1) Unzip epub into directory
# 2) Shrink images
# 3) Scrub extra data
#      remove <link rel="stylesheet"
#                   type="application/vnd.adobe-page-template+xml"
#                   href="page-template.xpgt"/>
#      TODO remove font?
#      TODO rename files
#
# TODO:
# - constrain width
# - add arrows for forward&backward chapter turns
#
# NOTE: it relies on various hacky regexes.

import sys
import getopt
import epub_extract

def main():
  opts, args = getopt.getopt(sys.argv[1:], "p:s:b:t:f:d:o:h:n:c:r:i:u:k:a:", [])

  def usage():
    print "-p: file containing prefix"
    print "-s: file containing suffix"
    print "-b: URL of book's page"
    print "-t: TOC file"
    print "-f: Frontpage file"
    print "-d: Directory prefix (of content, not prefix/suffix)"
    print "-o: Target directory"
    print "-h: file containing HTML to inject into header"
    print "-n: Title name"
    print "-c: A colophon file (e.g., the license). Multiple -c permitted."
    print "-r: How much to resize the images (as percentage; default is 50)."
    print "-i: Index file to use."
    print "-u: URL path of this book"
    print "-k: Copyright file"
    print "-a: Donation link"

  # it seems -i is unused in practice

  prefix_file = None
  suffix_file = None
  book_page = None
  toc_file = None
  front_file = None
  directory_prefix = ""
  target_directory = None
  headeradd_file = None
  book_title = ""
  colophon_files = []
  resize_percent = 50
  index_file = ""
  url_prefix = None
  copyright_file = None
  donation_link = None

  for o, a in opts:
    if o == "-p":
      prefix_file = a
    elif o == "-s":
      suffix_file = a
    elif o == "-b":
      book_page = a
    elif o == "-t":
      toc_file = a
    elif o == "-f":
      front_file = a
    elif o == "-d":
      directory_prefix = a
    elif o == "-o":
      target_directory = a
    elif o == "-h":
      headeradd_file = a
    elif o == "-n":
      book_title = a
    elif o == "-c":
      colophon_files.append(a)
    elif o == "-r":
      resize_percent = int(a)
    elif o == "-i":
      index_file = a
    elif o == "-u":
      url_prefix = a
    elif o == "-k":
      copyright_file = a
    elif o == "-a":
      donation_link = a
    else:
      usage()
      raise Exception('Unknown argument: ' + o + ':' + a)

  if (prefix_file == None or suffix_file == None or book_page == None or
      toc_file == None or front_file == None):
    usage()
    raise Exception('Incomplete parameter list')

  fragments = {}
  for filename, key in [
      (prefix_file, "prefix"),
      (suffix_file, "suffix"),
      (headeradd_file, "header_add")
  ]:
    with file(filename) as f:
      fragments[key] = "\n".join(f.readlines())

  epub_extract.process_pages(colophon_files, directory_prefix, toc_file,
                             book_title,
                             fragments, url_prefix, target_directory,
                             index_file, front_file, book_page, copyright_file,
                             donation_link)
  epub_extract.process_images_and_css(directory_prefix, resize_percent,
                                      target_directory)


if __name__ == '__main__':
  main()
