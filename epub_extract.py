
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
  """process_file(...) takes a filename referring to an input file which
     must be partly rewritten, and combined with other material, and
     does two things:

       * create a version of the contents with various inclusions and
         transformations applied
       * returns the links found in the source file, as well as title and
         index_file information also extracted

     Returns: a tuple: (links,
                        title,
                        index_file)
       where links is a set().

     Bugs: this function combines too many responsibilities
  """

  page_suffix = fragments["suffix"]
  # These re.subs are page-specific.
  #if filename <> "content.opf":

  if filename in pagecycle.keys():
    config_ps = {
      "prev": pagecycle[filename][0],
      "next": pagecycle[filename][1]
    }
  else:
    print("No PREV/NEXT for {}, defaulting to {}".format(filename, toc_file))
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

  def all_lines():
    with file(os.path.join(directory_prefix, filename)) as fd:
      for line in fd.readlines():
        if line == stylesheet_line:
          continue
        yield line

  details = {
    "book_title": book_title,
    "index_file": index_file
  }

  if target_directory is not None:
    # write_mode

    def gather_rewritten_contents():
      for line in all_lines():
        match = ignore_link.match(line)
        if match <> None:
          yield match.group(1) + match.group(2) + match.group(3)
        else:
          bodystart_match = body_start.match(line)
          bodyend_match = body_end.match(line)
          headerend_match = header_end.match(line)
          title_match = title_matcher.match(line)
          index_match = index_link.match(line)
          if bodystart_match <> None:
            yield line
            yield page_prefix
          elif bodyend_match <> None:
            yield page_suffix
            yield line
          elif headerend_match <> None:
            yield fragments["header_add"]
            yield line
          elif title_match <> None:
            yield line
            if details["book_title"] == "":
              details["book_title"] = title_match.group(1)
              print("Detected book title: {}".format(details["book_title"]))
          elif index_match <> None:
            yield line
            if details["index_file"] == "":
              details["index_file"] = index_match.group(1)
              print("Detected index file: {}".format(details["index_file"]))
          else:
            yield line

    with file(os.path.join(target_directory, filename), 'w') as f:
      for line in gather_rewritten_contents():
        f.write(line)

  links_to = set([])

  for line in all_lines():
    match = ignore_link.match(line)
    if match <> None:
      pass
    else:
      match = matcher_link.match(line)
      if match <> None:
        links_to.add(match.group(1))

  return links_to, details["book_title"], details["index_file"]


def generate_prefix(prefix, book_title, toc_file, book_page, index_file,
                    front_file, colophon_links, copyright_file, donation_link):
  config = {
    "booktitle": book_title,
    "toc": toc_file,
    "bookpage": book_page,
    "index": index_file,
    "frontpage": front_file,
    "copyright": copyright_file,
    "colophon_links": 'Colophon: {}'.format(', '.join(colophon_links)),
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
    anchor = "%{}%".format(key.upper())
    if value is not None:
      working_text = re.sub(anchor, value, working_text)
  return working_text


# populates pagecycle, based on info in toc.ncx
def extract_pagecycle(path):
  # maps a page of the book to its previous and next pages.
  # we wrap around: so the last page maps to the contents next, and the
  # contents maps to the last page previous.
  pagecycle = dict()

  script_path = os.path.join(os.path.dirname(__file__), "extract_pagecycle")
  cmd = "{} {}".format(script_path, path)
  files = string.split(commands.getoutput(cmd), '\n')

  print ("extracted files = {}".format(files))

  #store as tuples in pagecycle: page |-> (prev, next)
  for i in range(len(files)):
    print "doing {}: {}".format(i, files[i])
    page = files[i]
    prev = files[i - 1]
    next_ = files[(i + 1) % len(files)]
    pagecycle[page] = (prev, next_)

  print ("pagecycle = {}".format(pagecycle))

  return pagecycle

def extract_colophon_links(colo_file):
  match = re.search('^(.+_)?(.+)\.x?html?$', colo_file)
  if not (match and match.group(2) <> None):
    raise Exception(
      'The colophon file {} does not match the expected pattern.'.format(
        colo_file))

  # FIXME hardcoded formatting
  return '<a href="{}">{}</a>'.format(colo_file, match.group(2).title())


def process_images(directory_prefix, target_directory, path, resize_percent):
  img_path = os.path.join(directory_prefix, path)
  image_filenames = (
    map(os.path.basename, glob.glob(os.path.join(img_path, '*.jpg'))) +
    map(os.path.basename, glob.glob(os.path.join(img_path, '*.png')))
  )
  if target_directory is None:
    return

  img_path = os.path.join(target_directory, path)
  if not os.path.exists(img_path):
    os.makedirs(img_path)

  for filename in image_filenames:
    input_path = os.path.join(directory_prefix, path, filename)
    output_path = os.path.join(img_path, filename)
    rp = str(resize_percent)

    result = commands.getstatusoutput(
      "convert -resize {}% -quality 80 '{}' '{}'".format(
        rp, input_path, output_path
      )
    )
    print "converting {}:{}".format(filename, result)


def get_directory(directory_kind, directory_prefix, directory_heuristics):
  for directory_heuristic in directory_heuristics:
    if os.path.exists(os.path.join(directory_prefix, directory_heuristic)):
      print "Detected {} directory: {}".format(directory_kind,
                                               directory_heuristic)
      return directory_heuristic

  raise Exception('Could not find {} directory'.format(directory_kind))


def process_images_and_css(directory_prefix, resize_percent, target_directory):
  images_directory = get_directory('Images', directory_prefix,
                                   ['images', 'Images', 'image'])
  print "\nNow converting images. Resize is {}%".format(resize_percent)
  process_images(directory_prefix, target_directory, images_directory + "/",
                 resize_percent)

  css_directory = get_directory('CSS', directory_prefix, ['css'])

  result = commands.getstatusoutput(
    "cp -r {} {}".format(
      os.path.join(directory_prefix, css_directory),
      os.path.join(target_directory, css_directory)
    )
  )

  print "copying CSS directory ({}): {}".format(css_directory, result)


def process_pages(colophon_files, directory_prefix, toc_file, book_title,
                  fragments, url_prefix, target_directory,
                  index_file, front_file, book_page,
                  copyright_file, donation_link):
  files_done = 0

  colophon_links = [ extract_colophon_links(colo_file)
                     for colo_file in colophon_files ]
  pagecycle = extract_pagecycle(directory_prefix)

  opf_path = os.path.join(os.path.dirname(toc_file), 'content.opf')
  # List of HTML files
  processed_pages = set([])
  pages_to_process = set([toc_file, opf_path])

  while len(pages_to_process) > 0:
    filename = pages_to_process.pop()
    print "processing {}".format(filename)
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

  print "processed {} files".format(files_done)

