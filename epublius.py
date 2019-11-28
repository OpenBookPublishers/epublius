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
import re
import glob
import os
import commands
#import subprocess
import string
import urllib
import breadcrumbs

#include both HTML and CSS files
matcher_link = re.compile(
  "^.* href=\"([a-zA-Z0-9_.-]+?\.(html|css|xhtml))(#.+)?\".*$")

title_matcher = re.compile("^.*<title>(.+)</title>.*$")

#filter out the "part" pages
ignore_link = re.compile(
  "^(.*)<a.+href=\"\d+_part\d+\.x?html\".*?>(.+)</a>(.*)$")

body_start = re.compile("^.*<body ?.*>.*$") #FIXME dangerous
body_end   = re.compile("^.*</body>.*$")
header_end = re.compile("^.*</head>.*$")
index_link = re.compile(
  "^.*<a.+href=\"((\d+_)?[Ii]ndex\.x?html)\".*?>(INDEX|Index)</a>.*$")

stylesheet_line = ('''<link rel="stylesheet" ''' +
                   '''type="application/vnd.adobe-page-template+xml"''' +
                   ''' href="page-template.xpgt"/>''')

def process_file(filename, book_title, pagecycle, fragments,
                 toc_file, url_prefix,
                 directory_prefix,
                 target_directory,
                 index_file):
  page_suffix = fragments["suffix"]
  # These re.subs are page-specific.
  #if filename <> "content.opf":

  if filename in pagecycle.keys():
    config_ps = {
      "prev": pagecycle[filename][0],
      "next": pagecycle[filename][1]
    }
  else:
    print "No PREV/NEXT for " + filename + ", defaulting to " + toc_file
    config_ps = {
      "prev": toc_file,
      "next": toc_file
    }
  page_suffix = render_template(page_suffix, config_ps)

  page_prefix = fragments["prefix"]

  # used for searching within the book
  if url_prefix.endswith("/"):
    slashed_url_prefix = url_prefix
  else:
    slashed_url_prefix = url_prefix + "/"

  config_pp = {
    "this_page_url_prefix": slashed_url_prefix + "*",
    "this_page_url": slashed_url_prefix + filename,
    "this_page_url_encoded": urllib.quote(slashed_url_prefix + filename,
                                          safe='')
  }
  page_prefix = render_template(page_prefix, config_pp)

  links_to = set([])
  fd = open(directory_prefix + filename)
  new_contents = []

  if target_directory == None:
    write_mode = False
  else:
    write_mode = True

  for line in fd.readlines():
    if line == stylesheet_line:
      continue
    match = ignore_link.match(line)
    if match <> None:
      if write_mode:
        new_contents.append(match.group(1) + match.group(2) + match.group(3))
    else:
      match = matcher_link.match(line)
      if match <> None:
        links_to.add(match.group(1))

      if not write_mode:
        continue

      bodystart_match = body_start.match(line)
      bodyend_match = body_end.match(line)
      headerend_match = header_end.match(line)
      title_match = title_matcher.match(line)
      index_match = index_link.match(line)
      if bodystart_match <> None:
        new_contents.append(line)
        new_contents.append(page_prefix)
      elif bodyend_match <> None:
        new_contents.append(page_suffix)
        new_contents.append(line)
      elif headerend_match <> None:
        new_contents.append(fragments["header_add"])
        new_contents.append(line)
      elif title_match <> None:
        new_contents.append(line)
        if book_title == "":
          book_title = title_match.group(1)
          print "Detected book title:" + book_title
      elif index_match <> None:
        new_contents.append(line)
        if index_file == "":
          index_file = index_match.group(1)
          print "Detected index file:" + index_file
      else:
        new_contents.append(line)

  fd.close()

  if write_mode:
    fd = open(target_directory + filename, 'w')
    fd.writelines(new_contents)
    fd.close()

  return links_to, book_title, index_file


def generate_prefix(prefix, book_title, toc_file, book_page, index_file,
                    front_file, colophon_links, copyright_file, donation_link):
  config = {
    "booktitle": book_title,
    "toc": toc_file,
    "bookpage": book_page,
    "index": index_file,
    "frontpage": front_file,
    "copyright": copyright_file,
    "colophon_links": 'Colophon: ' + ', '.join(colophon_links),
    "donate": donation_link
  }

  return render_template(prefix, config)


def render_template(template, config):
  """
  Take some text like `Dear %FIRSTNAME% %SURNAME%, ...' and
  a dictionary of the form:
  {
    "firstname": "John",
    "surname": "Smith"
  }
  and interpolate the relevant items (capitalising the keyword).
  """
  working_text = template
  for key, value in config.iteritems():
    anchor = "%" + key.upper() + "%"
    if value is not None:
      working_text = re.sub(anchor, value, working_text)
  return working_text


# populates pagecycle, based on info in toc.ncx
def extract_pagecycle(path):
  # maps a page of the book to its previous and next pages.
  # we wrap around: so the last page maps to the contents next, and the
  # contents maps to the last page previous.
  pagecycle = dict()

  files = string.split(commands.getoutput(
    "grep 'content src' " + path + "toc.ncx " +
    "| perl -pe 's/^.+<text>(.+?)<\/text>.+content src=\"(.+?)(#.*?)?\".+$/$2/' " +
    "| uniq"), '\n'
  )

  print ("extracted files = " + str(files))

  #store as tuples in pagecycle: page |-> (prev, next)
  for i in range(len(files)):
    print "doing " + str(i) + ": " + files[i]
    page = files[i]
    prev = files[i - 1]
    next_ = files[(i + 1) % len(files)]
    pagecycle[page] = (prev, next_)

  print ("pagecycle = " + str(pagecycle))

  return pagecycle

def extract_colophon_links(colo_file):
  match = re.search('^(.+_)?(.+)\.x?html?$', colo_file)
  if not (match and match.group(2) <> None):
    raise Exception('The colophon file ' + colo_file +
                      ' does not match the expected pattern.')

  # FIXME hardcoded formatting
  return '<a href="' + colo_file + '">' + match.group(2).title() + '</a>'


def process_images(directory_prefix, target_directory, path, resize_percent):
  image_filenames = (
    map(os.path.basename, glob.glob(directory_prefix + path + '*.jpg')) +
    map(os.path.basename, glob.glob(directory_prefix + path + '*.png'))
  )
  if target_directory <> None:
    try: os.makedirs(target_directory + path)
    except: pass
    for filename in image_filenames:
      result = commands.getstatusoutput(
        "convert -resize " + str(resize_percent) + "% -quality 80 " +
        "'" + directory_prefix + path + filename + "'" +
        " '" + target_directory + path + filename + "'"
      )
      print "converting " + filename + ":" + str(result)


def get_directory(directory_kind, directory_prefix, directory_heuristics):
  for directory_heuristic in directory_heuristics:
    if os.path.exists(directory_prefix + directory_heuristic):
      print "Detected " + directory_kind + " directory: " + directory_heuristic
      return directory_heuristic

  raise Exception('Could not find ' + directory_kind + ' directory')


def process_images_and_css(directory_prefix, resize_percent, target_directory):
  images_directory = get_directory('Images', directory_prefix,
                                   ['images', 'Images', 'image'])
  print
  print "Now converting images. Resize is " + str(resize_percent) + "%"
  process_images(directory_prefix, target_directory, images_directory + "/",
                 resize_percent)

  css_directory = get_directory('CSS', directory_prefix, ['css'])
  result = commands.getstatusoutput("cp -r " + directory_prefix + "/" +
                                    css_directory +
                                    " " + target_directory + "/" +
                                    css_directory)

  print "copying CSS directory (" + css_directory + "):" + str(result)


def process_pages(colophon_files, directory_prefix, toc_file, book_title,
                  fragments, url_prefix, target_directory,
                  index_file, front_file, book_page,
                  copyright_file, donation_link):
  files_done = 0

  colophon_links = [ extract_colophon_links(colo_file)
                     for colo_file in colophon_files ]
  pagecycle = extract_pagecycle(directory_prefix)

  # List of HTML files
  processed_pages = set([])
  pages_to_process = set([toc_file, os.path.dirname(toc_file) + 'content.opf'])

  while len(pages_to_process) > 0:
    filename = pages_to_process.pop()
    print "processing " + filename
    new_links, book_title, index_file = process_file(
      filename, book_title,
      pagecycle, fragments, toc_file, url_prefix,
      directory_prefix,
      target_directory, index_file)

    # the first file is processed twice.
    # first time is to extract values, and the second time is to use them.
    if (files_done == 0):
      pages_to_process.add(filename)

      # Process files which aren't linked-to by the TOC,
      # such as the Cover and the Colophon.
      pages_to_process.add(front_file)
      for colo_file in colophon_files:
        pages_to_process.add(colo_file)
      fragments["prefix"] = generate_prefix(
        fragments["prefix"], book_title, toc_file, book_page,
        index_file, front_file, colophon_links,
        copyright_file, donation_link)

    else:
      processed_pages.add(filename)
      pages_to_process = pages_to_process.union(new_links)
      pages_to_process.difference_update(processed_pages)

    files_done += 1
    breadcrumbs.process_file(filename)

  print "processed " + str(files_done) + " files"



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

  process_pages(colophon_files, directory_prefix, toc_file, book_title,
                fragments, url_prefix, target_directory,
                index_file, front_file, book_page, copyright_file,
                donation_link)
  process_images_and_css(directory_prefix, resize_percent, target_directory)


if __name__ == '__main__':
  main()
