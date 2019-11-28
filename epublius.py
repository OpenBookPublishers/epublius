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
# Example usage: ./epublius.py -p prefix -s suffix -f 02_title.html -t 06_toc.html -b https://www.openbookpublishers.com/product/97 -d ../epub/OEBPS/ -o ../epub/new/ -h header_add
#
# What it does:
# 1) Unzip epub into directory
# 2) Shrink images
# 3) Scrub extra data
#      remove <link rel="stylesheet" type="application/vnd.adobe-page-template+xml" href="page-template.xpgt"/>
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
    print "-c: A colophon file (e.g., the license). There may be multiple -c parameters."
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

  if target_directory == None:
    write_mode = False
  else:
    write_mode = True

  prefix_fd = open(prefix_file)
  prefix = "\n".join(prefix_fd.readlines())
  prefix_fd.close()

  suffix_fd = open(suffix_file)
  suffix = "\n".join(suffix_fd.readlines())
  suffix_fd.close()

  headeradd_fd = open(headeradd_file)
  header_add = headeradd_fd.readlines()
  headeradd_fd.close()

  #include both HTML and CSS files
  matcher_link = re.compile("^.* href=\"([a-zA-Z0-9_.-]+?\.(html|css|xhtml))(#.+)?\".*$")

  title_matcher = re.compile("^.*<title>(.+)</title>.*$")

  #filter out the "part" pages
  ignore_link = re.compile("^(.*)<a.+href=\"\d+_part\d+\.x?html\".*?>(.+)</a>(.*)$")

  body_start = re.compile("^.*<body ?.*>.*$") #FIXME dangerous
  body_end = re.compile("^.*</body>.*$")
  header_end = re.compile("^.*</head>.*$")
  index_link = re.compile("^.*<a.+href=\"((\d+_)?[Ii]ndex\.x?html)\".*?>(INDEX|Index)</a>.*$")

  files_done = 0

  #maps a page of the book to its previous and next pages. we wrap around: so the
  #last page maps to the contents next, and the contents maps to the last page
  #previous.
  pagecycle = dict()

  #populates pagecycle, based on info in toc.ncx
  def extract_pagecycle(path):
    # from http://stackoverflow.com/questions/19243020/in-python-get-the-output-of-system-command-as-a-string?lq=1
    #cmd = "grep 'content src' OEBPS/toc.ncx | perl -pe 's/^.+<text>(.+?)<\/text>.+content src="(.+?)(#.*?)?".+$/$1\t$2/'"
    #cmd = ("/usr/bin/grep 'content src' " + path + "toc.ncx | " +
    #       "/usr/bin/perl -pe 's/^.+<text>(.+?)<\/text>.+content src=\"(.+?)(#.*?)?\".+$/$2/' | " +
    #       "/usr/bin/uniq")

    #print ("cmd = " + cmd)

    #proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    #files_str = proc.stdout.read()

    #factor out unique html files into a list
    #files = files_str.split()

    files = string.split(commands.getoutput("grep 'content src' " + path + "toc.ncx " +
                                             "| perl -pe 's/^.+<text>(.+?)<\/text>.+content src=\"(.+?)(#.*?)?\".+$/$2/' " +
                                             "| uniq"), '\n')

    print ("extracted files = " + str(files))

    #store as tuples in pagecycle: page |-> (prev, next)
    for i in range(len(files)):
      print "doing " + str(i) + ": " + files[i]
      page = files[i]
      prev = files[i - 1]
      next = files[(i + 1) % len(files)]
      pagecycle[page] = (prev, next)

    print ("pagecycle = " + str(pagecycle))

  def process_file(filename, book_title):
    page_suffix = suffix
    # These re.subs are page-specific.
    #if filename <> "content.opf":
    if filename in pagecycle.keys():
      page_suffix = re.sub("%PREV%", pagecycle[filename][0], page_suffix)
      page_suffix = re.sub("%NEXT%", pagecycle[filename][1], page_suffix)
    else:
      print "No PREV/NEXT for " + filename + ", defaulting to " + toc_file
      page_suffix = re.sub("%PREV%", toc_file, page_suffix)
      page_suffix = re.sub("%NEXT%", toc_file, page_suffix)

    page_prefix = prefix
    # used for searching within the book
    if url_prefix.endswith("/"):
      slashed_url_prefix = url_prefix
    else:
      slashed_url_prefix = url_prefix + "/"
    page_prefix = re.sub("%THIS_PAGE_URL_PREFIX%", slashed_url_prefix + "*", page_prefix)
    # used for translating this page
    page_prefix = re.sub("%THIS_PAGE_URL%", slashed_url_prefix + filename, page_prefix)
    page_prefix = re.sub("%THIS_PAGE_URL_ENCODED%", urllib.quote(slashed_url_prefix + filename, safe=''), page_prefix)

    links_to = set([])
    fd = open(directory_prefix + filename)
    new_contents = []
    for line in fd.readlines():
      if line <> '<link rel="stylesheet" type="application/vnd.adobe-page-template+xml" href="page-template.xpgt"/>':
        match = ignore_link.match(line)
        if match <> None:
          if write_mode:
            new_contents.append(match.group(1) + match.group(2) + match.group(3))
        else:
          match = matcher_link.match(line)
          if match <> None:
            links_to.add(match.group(1))

          if write_mode:
            bodystart_match = body_start.match(line)
            bodyend_match = body_end.match(line)
            headerend_match = header_end.match(line)
            title_match = title_matcher.match(line)
            index_match = index_link.match(line)
            if bodystart_match <> None:
              new_contents.append(line)
              # new_contents.append('<body onload="loader();">\n')

              # new_contents = new_contents + page_prefix
              new_contents.append(page_prefix)
            elif bodyend_match <> None:
              # new_contents = new_contents + page_suffix
              new_contents.append(page_suffix)
              new_contents.append(line)
            elif headerend_match <> None:
              new_contents = new_contents + header_add
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

    return links_to, book_title

  # List of HTML files
  processed_pages = set([])
  pages_to_process = set([toc_file, os.path.dirname(toc_file) + 'content.opf'])

  colophon_links = []
  for colo_file in colophon_files:
    match = re.search('^(.+_)?(.+)\.x?html?$', colo_file)
    if match and match.group(2) <> None:
      #FIXME hardcoded formatting
      colophon_links.append('<a href="' + colo_file + '">' + match.group(2).title() + '</a>')
    else:
      raise Exception('The colophon file ' + colo_file + ' does not match the expected pattern.')

  extract_pagecycle(directory_prefix)

  while len(pages_to_process) > 0:
    filename = pages_to_process.pop()
    print "processing " + filename
    new_links, book_title = process_file(filename, book_title)

    # the first file is processed twice.
    # first time is to extract values, and the second time is to use them.
    if (files_done == 0):
      pages_to_process.add(filename)

      # Process files which aren't linked-to by the TOC,
      # such as the Cover and the Colophon.
      pages_to_process.add(front_file)
      for colo_file in colophon_files:
        pages_to_process.add(colo_file)
      prefix = re.sub("%BOOKTITLE%", book_title, prefix)
      prefix = re.sub("%TOC%", toc_file, prefix)
      prefix = re.sub("%BOOKPAGE%", book_page, prefix)
      prefix = re.sub("%INDEX%", index_file, prefix)
      prefix = re.sub("%FRONTPAGE%", front_file, prefix)
      prefix = re.sub("%COLOPHON_LINKS%", 'Colophon: ' +
                      ', '.join(colophon_links), prefix)

      prefix = re.sub("%COPYRIGHT%", copyright_file, prefix)
      if donation_link != None: prefix = re.sub("%DONATE%",
                                                donation_link, prefix)

    else:
      processed_pages.add(filename)
      pages_to_process = pages_to_process.union(new_links)
      pages_to_process.difference_update(processed_pages)

    files_done += 1

  print "processed " + str(files_done) + " files"
  #print "processed_pages=" + str(processed_pages)
  #print "pages_to_process=" + str(pages_to_process)

  def process_images(directory_prefix, target_directory, path):
    image_filenames = (map(os.path.basename, glob.glob(directory_prefix + path + '*.jpg')) +
                       map(os.path.basename, glob.glob(directory_prefix + path + '*.png')))
    if target_directory <> None:
      try: os.makedirs(target_directory + path)
      except: pass
      for filename in image_filenames:
        result = commands.getstatusoutput("convert -resize " + str(resize_percent) + "% -quality 80 " +
                                          "'" + directory_prefix + path + filename + "'" +
                                          " '" + target_directory + path + filename + "'")
        print "converting " + filename + ":" + str(result)

  print
  print "Now converting images. Resize is " + str(resize_percent) + "%"

  #This follows the style of get_file in epublius_wrapper.py
  def get_directory (directory_kind, directory_prefix, directory_heuristics):
    directory = None
    for directory_heuristic in directory_heuristics:
      if os.path.exists(directory_prefix + directory_heuristic):
        directory = directory_heuristic
        print "Detected " + directory_kind + " directory: " + directory
        break

    if directory == None:
      raise Exception('Could not find ' + directory_kind + ' directory')

    return directory

  images_directory = get_directory('Images', directory_prefix, ['images', 'Images', 'image'])
  process_images(directory_prefix, target_directory, images_directory + "/")

  css_directory = get_directory('CSS', directory_prefix, ['css'])
  result = commands.getstatusoutput("cp -r " + directory_prefix + "/" + css_directory +
                                    " " + target_directory + "/" + css_directory)
  print "copying CSS directory (" + css_directory + "):" + str(result)

if __name__ == '__main__':
  main()
