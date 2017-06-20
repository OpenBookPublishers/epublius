#!/usr/bin/python
#
# ePublius wrapper
# Discovers the values of parameters to be given to epublius.py.
# Currently works for -f, -t and -l.
# Uses toc.ncx to get these values. I also rely on matching
# filenames, but these often vary wildly. FIXME change the process to rely solely on toc.ncx
#
# (c) Nik Sultana, Open Book Publishers, September 2013
# Use of this software is governed by the terms of the GPLv3 -- see LICENSE.
#
# Example usage: ./epublius_wrapper.py -p prefix -s suffix -h header_add -b https://www.openbookpublishers.com/product/97 -f 9781906924737_Oral_Literature_in_Africa.epub -o test
# or: ./epublius_wrapper.py -p prefix -s suffix -h header_add -b https://www.openbookpublishers.com/product/98/women-in-nineteenth-century-russia--lives-and-culture -f testfiles/Women_in_Russia.epub -o WIR2 -n "Women in Russia"
# or, with variable image resizing: ./epublius_wrapper.py -p prefix -s suffix -h header_add -b https://www.openbookpublishers.com/product/215/ -f 9781783740031_Tacitus_Annals.epub -o TA -n "Tacitus, Annals, 15.20-23, 33-45. Latin Text, Study Aids with Vocabulary, and Commentary" -r 80
#
# What it does:
# - create temp directory
# - unzip epub into it
# - detect values of parameters to be passed to epublius.py.
# - run epublius
# - remove temp directory

import random
import time
import os
import sys
import getopt
import glob
import commands
import shutil
import re
import string

TMPDIR = "/tmp" #FIXME hardcoded path
random.seed(str(time.gmtime()))

opts, args = getopt.getopt(sys.argv[1:], "p:s:h:b:f:o:n:z:cr:e:i:u:a:t:", [])

def usage():
  print "-p: file containing prefix"
  print "-s: file containing suffix"
  print "-h: file containing HTML to inject into header"
  print "-b: URL of book's page"
  print "-f: ePub file (or contents, if -z is used)"
  print "-o: Target directory"
  print "-n: Book name"
  print "-z: Target of -f parameter is an unzipped ePub file"
  print "-c: Book doesn't have a cover"
  print "-r: How much to resize the images (as percentage; default is 50)."
  print "-e: Location of the ePublius script."
  print "-i: Force the use of a particular index file. This parameter will simply be passed on to the epublius script."
  print "-u: URL path of this book"
  print "-a: Donation link"
  print "-t: Directory containing the template files (CSS and JS)"

prefix_file = None
suffix_file = None
headeradd_file = None
book_page = None
epub_file = None
target_directory = None
book_title = None
unzipped_ePub = False
no_cover = False
resize_percent = None
ePublius_path = "."
index_to_use = None
url_prefix = None
donation_link = None
template_dir = "."

for o, a in opts:
  if o == "-p":
    prefix_file = a
  elif o == "-s":
    suffix_file = a
  elif o == "-h":
    headeradd_file = a
  elif o == "-b":
    book_page = a
  elif o == "-f":
    epub_file = a
  elif o == "-o":
    target_directory = a
  elif o == "-n":
    book_title = a
  elif o == "-z":
    unzipped_ePub = True
  elif o == "-c":
    no_cover = True
  elif o == "-r":
    resize_percent = int(a)
  elif o == "-e":
    ePublius_path = a
  elif o == "-i":
    index_to_use = a
  elif o == "-u":
    url_prefix = a
  elif o == "-a":
    donation_link = a
  elif o == "-t":
    template_dir = a
  else:
    usage()
    raise Exception('Unknown argument: ' + o + ':' + a)

if (prefix_file == None or suffix_file == None or headeradd_file == None or
    book_page == None or epub_file == None or target_directory == None or
    url_prefix == None):
  usage()
  raise Exception('Incomplete parameter list')

#Transform index_to_use into a parameter for the epublius script.
if index_to_use == None:
  index_to_use = "" #No parameter
else:
  print "Will use index: " + index_to_use
  index_to_use = " -i " + index_to_use + " "

def create_tmpdir():
  tmpdir = None
  while (tmpdir == None):
    tmpdir_try = TMPDIR + "/epublius_" + str(random.getrandbits(24)) + "_tmp/"
    if os.path.exists(tmpdir_try) == False:
      os.makedirs(tmpdir_try)
      tmpdir = tmpdir_try
  return tmpdir

print "epub_file = " + epub_file

if unzipped_ePub:
  tmpdir = epub_file
else:
  tmpdir = create_tmpdir()
  _, output = commands.getstatusoutput("unzip " + epub_file + " -d " + tmpdir)
  print output

_, path = commands.getstatusoutput("find " + tmpdir + " -name toc.ncx")
path = (string.split(path, '\n'))[0] #In case there were multiple finds, we use the first
print "Temporary directory: " + tmpdir
path = os.path.dirname(path) + "/"
print "Expecting to find cover file at: " + path

def get_file (file_kind, file_heuristics):
  file = None
  for file_heuristic in file_heuristics:
    file_attempt = glob.glob(path + file_heuristic)
    #print "Attempting " + path + file_heuristic + " : " + str(file_attempt)
    if len(file_attempt) == 1:
      file = os.path.basename(file_attempt[0])
      print "Detected " + file_kind + " file: " + file
      break
    elif len(file_attempt) > 1:
      #This is suspicious, since there should be only one match.
      print "Possible problem: detected " + file_kind + " files:" + str(file_attempt) + " using glob " + file_heuristic

  if file == None:
    if not unzipped_ePub:
      shutil.rmtree(tmpdir)
    raise Exception('Could not find ' + file_kind + ' file')

  return file


content_files = string.split(commands.getoutput("grep \"<item id=\" " + path + "content.opf " +
                                                "| grep 'media-type=\"application/xhtml+xml\"'" +
                                                "| perl -pe 's/^.+href=\"(.+?)\".+$/$1/'"),
                             '\n')
colophon_files = []
toc_file = None
title_file = None
copyright_file = None
for content_file in content_files:
  #FIXME could put these heuristics into a config file, or given them at the command line.
  match_cover = re.search('(_cover.html|cover.html|_Cover.html|Front-cover.xhtml|front-cover.xhtml|00-cover.xhtml)', content_file)
  if match_cover and title_file == None:
    title_file = content_file

  #FIXME could put these heuristics into a config file, or given them at the command line.
  match_toc = re.search('(_toc.html|toc.html|_Contents.html|_Content.html|_Tableofcontent.html|Contents-digital.xhtml|contents.xhtml|Contents.xhtml|Main-text-1.xhtml)', content_file)
  #NOTE sometimes the files might be contained within a subdirectory -- e.g., 'Text/toc.html' in the case of Yates Annual.
  #     this is considered as a special case and handled manually, to avoid complicated this code.
  if match_toc and toc_file == None:
    toc_file = content_file
    #Cover should always precede the TOC, so once we find the TOC we can break out of the loop.
    break
  else:
    colophon_files.append(content_file)

  match_copyright = re.search('(copyright.xhtml|Copyright.xhtml|copyright.html)', content_file)
  if match_copyright and copyright_file == None:
    copyright_file = content_file

if no_cover:
  title_file = toc_file

print "found toc_file: " + str(toc_file)
print "found title_file: " + str(title_file)
print "found copyright_file: " + str(copyright_file)

print "colophon_files=" + str(colophon_files)

#Remove Cover from colophon_files, to avoid it being shown twice in the menu
# (as an individual link, and as part of the colophon).
del colophon_files[colophon_files.index(title_file)]

target_directory = target_directory + "/" #FIXME check for this
if not unzipped_ePub:
  os.makedirs(target_directory)

# We previously used title_file as the main page, but switched to toc_file in 2016.
commands.getstatusoutput("cp " + path + "/" + toc_file + " " + path + "/" + "main.html")
title_file = "main.html"

book_title_arg = ""
if book_title <> None:
  book_title_arg = "-n \"" + book_title + "\""

if donation_link == None: donation_link = ""
else: donation_link = " -a '" + donation_link + "'"

cmd = (ePublius_path + "/epublius.py -p " + prefix_file + " -s " + suffix_file +
       " -h " + headeradd_file + " -b " + book_page + " -f " + title_file +
       " -k " + copyright_file +
       index_to_use +
       " -u " + url_prefix +
       donation_link +
       " -t " + toc_file + " -d " + path + " -o " + target_directory  +
       ''.join(map(lambda s: ' -c ' + s, colophon_files)))

if resize_percent <> None:
 cmd += ' -r ' + str(resize_percent)

_, output = commands.getstatusoutput(cmd + ' ' + book_title_arg)
print output

# We recopy the file, since when we earlier copied the file it had not yet been
# processed by epublius, but now it has.
commands.getstatusoutput("cp " + target_directory + "/" + toc_file + " " + target_directory + "/" + "main.html")

cmd = ("cp " + template_dir + "/html-style.css" +
       " " + target_directory + "/css/ && " +
       "cp " + template_dir + "/JS/*" +
       " " + target_directory + "/")
print "Copying JS and CSS via command: " + cmd
_, output = commands.getstatusoutput(cmd)

## Append left and right padding requirement to CSS file.
#cmd = ("echo 'body { padding : 0px 40px 0px 40px; }' >> " + path + "/css/idGeneratedStyles_0.css")
#print "Appending CSS info via command: " + cmd
#_, output = commands.getstatusoutput(cmd)
##

if not unzipped_ePub:
  shutil.rmtree(tmpdir)
