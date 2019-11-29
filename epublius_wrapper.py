#!/usr/bin/python2
#
# ePublius wrapper

# Discovers the values of parameters to be given to epublius.py.

# Currently works for -f, -t and -l.
# Uses toc.ncx to get these values. I also rely on matching

# filenames, but these often vary wildly.
# FIXME change the process to rely solely on toc.ncx
#
# (c) Nik Sultana, Open Book Publishers, September 2013
# Use of this software is governed by the terms of the GPLv3 -- see LICENSE.
#
# Example usage: ./epublius_wrapper.py -p prefix -s suffix \
#   -h header_add -b https://www.openbookpublishers.com/product/97 \
#   -f /home/nik/OBP/code/epub/9781906924737_Oral_Literature_in_Africa.epub \
#   -o test \
#   -u https://www.openbookpublishers.com/product/000
#
# or: ./epublius_wrapper.py -p prefix -s suffix -h header_add \
#   -b https://www.openbookpublishers.com/product/98/women-in-nineteenth-century-russia--lives-and-culture \
#   -f testfiles/Women_in_Russia.epub -o WIR2 -n "Women in Russia"
#
# or, with variable image resizing:
#    ./epublius_wrapper.py -p prefix -s suffix -h header_add \
#    -b https://www.openbookpublishers.com/product/215/ \
#    -f 9781783740031_Tacitus_Annals.epub -o TA \
#    -n "Tacitus, Annals, 15.20-23, 33-45. Latin Text, Study Aids with Vocabulary, and Commentary" \
#    -r 80
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
import glob
import subprocess
import commands
import shutil
import re
import string
import argparse

TMPDIR = "/tmp" #FIXME hardcoded path
random.seed(str(time.gmtime()))

def fake_command(s):
  args = s.split(" ")
  output = subprocess.check_output(args)
  return 0, output


def main():

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
                      default = None,
                      help = 'Book name')

  parser.add_argument('-z', '--zip',
                      help = 'Target of -f parameter is an unzipped ' \
                             'ePub file',
                      default = False,
                      action = "store_true")

  parser.add_argument('-c', '--cover',
                      help = 'Book doesn\'t have a cover',
                      default = False,
                      action="store_true")

  parser.add_argument('-r', '--resample',
                      help = 'Resample image (as percentage; ' \
                             'default is 50, no resampling is 100).',
                      default = None,
                      type = int)

  parser.add_argument('-e', '--epublish',
                      help = 'Location of the ePublius script.',
                      default = '.')

  parser.add_argument('-i', '--index',
                      help = 'Force the use of a particular index ' \
                             'file. This parameter will simply be ' \
                             'passed on to the epublius script.',
                      default = None)

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

  args = parser.parse_args()

  ## TODO We should use a dictionary instead of so many variables.
  ## Keeping the original notation as legacy code.
  prefix_file = args.prefix
  suffix_file = args.suffix
  headeradd_file = args.header
  book_page = args.book
  epub_file = args.file
  target_directory = args.output
  book_title = args.name
  unzipped_ePub = args.zip
  no_cover = args.cover
  resize_percent = args.resample
  ePublius_path = args.epublish
  index_to_use = args.index
  url_prefix = args.url
  donation_link = args.donation
  template_dir = args.template

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
    _, output = fake_command("unzip " + epub_file + " -d " + tmpdir)
    print output

  _, path = fake_command("find " + tmpdir + " -name toc.ncx")

  # In case there were multiple finds, we use the first:
  path = (string.split(path, '\n'))[0]
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
        print ("Possible problem: detected " + file_kind + " files:" +
               str(file_attempt) + " using glob " + file_heuristic)

    if file == None:
      if not unzipped_ePub:
        shutil.rmtree(tmpdir)
      raise Exception('Could not find ' + file_kind + ' file')

    return file


  content_files = string.split(commands.getoutput(
    "grep \"<item id=\" " + path + "content.opf " +
    "| grep 'media-type=\"application/xhtml+xml\"'" +
    "| perl -pe 's/^.+href=\"(.+?)\".+$/$1/'"),
                               '\n')
  colophon_files = []
  toc_file = None
  title_file = None
  copyright_file = None
  for content_file in content_files:
    # FIXME:
    # could put these heuristics into a config file, or given them
    # at the command line.
    match_cover = re.search('(_cover.html|cover.html|_Cover.html|Front-cover.xhtml|front-cover.xhtml|00-cover.xhtml)', content_file)
    if match_cover and title_file == None:
      title_file = content_file

    # FIXME:
    # could put these heuristics into a config file, or given them
    # at the command line.
    match_toc = re.search('(_toc.html|toc.html|_Contents.html|_Content.html|_Tableofcontent.html|Contents-digital.xhtml|contents.xhtml|Contents.xhtml|Main-text-1.xhtml|Resemblance-and-Representation.xhtml)', content_file)

    # NOTE
    # sometimes the files might be contained within a subdirectory
    #   -- e.g., 'Text/toc.html' in the case of Yates Annual.
    #     this is considered as a special case and handled manually, 
    #     to avoid complicated this code.
    if match_toc and toc_file == None:
      toc_file = content_file
      #Cover should always precede the TOC, so once we find the TOC we can break out of the loop.
      break
    else:
      colophon_files.append(content_file)

    match_copyright = re.search('(copyright.xhtml|Copyright.xhtml|copyright.html)', content_file) #Copyright.xhtml added by Bianca on 2016-10-18
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

  # We previously used title_file as the main page, but switched to
  # toc_file in 2016.

  fake_command("cp " + path + "/" + toc_file +
                           " " + path + "/" + "main.html")
  title_file = "main.html"

  book_title_arg = ""
  if book_title <> None:
    book_title_arg = "-n \"" + book_title + "\""

  if donation_link == None: donation_link = ""
  else: donation_link = " -a '" + donation_link + "'"

  copyright_arg = copyright_file + index_to_use
  url_arg = url_prefix + donation_link
  exe_path = os.path.join(ePublius_path, "epublius.py")

  cmd = (exe_path +
         " -p " + prefix_file +
         " -s " + suffix_file +
         " -h " + headeradd_file +
         " -b " + book_page +
         " -f " + title_file +
         " -k " + copyright_arg +
         " -u " + url_arg +
         " -t " + toc_file +
         " -d " + path +
         " -o " + target_directory +
         ''.join(map(lambda s: ' -c ' + s, colophon_files)))

  if resize_percent <> None:
   cmd += ' -r ' + str(resize_percent)

  _, output = fake_command(cmd + ' ' + book_title_arg)
  print output

  # We recopy the file, since when we earlier copied the file it had
  # not yet been processed by epublius, but now it has.
  fake_command("cp " + target_directory + "/" + toc_file
                           + " " + target_directory + "/" + "main.html")
  # add html charset meta tag based on original encoding
  cmd = ("sed -i \"s/<head>/<head>\\n    <meta $(awk 'NR==1' " +
         target_directory + "/" + toc_file +
         " |awk '{print $3}' | sed 's/encoding/charset/')>/\" " +
         target_directory + "/main.html")
  print "Adding charset to main.html: " + cmd
  commands.getoutput(cmd)

  cmd = ("cp " + template_dir + "/html-style.css" +
         " " + target_directory + "/css/ && " +
         "cp " + template_dir + "/JS/*" +
         " " + target_directory + "/")
  print "Copying JS and CSS via command: " + cmd
  _, output = commands.getstatusoutput(cmd)

  cmd = ("cp -r " + template_dir + "/logo" +
         " " + target_directory + "/")

  print "Copying logo folder via command: " + cmd
  _, output = fake_command(cmd)

  ## Append left and right padding requirement to CSS file.
  # cmd = ("echo 'body { padding : 0px 40px 0px 40px; }' >> "
  #          + path + "/css/idGeneratedStyles_0.css")
  #print "Appending CSS info via command: " + cmd
  #_, output = fake_command(cmd)
  ##

  if not unzipped_ePub:
    shutil.rmtree(tmpdir)

if __name__ == '__main__':
  main()
