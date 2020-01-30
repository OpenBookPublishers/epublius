#!/usr/bin/python2

import os
import subprocess
import shutil
import epub_extract
import tempfile
from epublius import epublius
from epublius import parse_tools
from epublius import metadata
from epublius import output_html


def main():

  # TODO
  # to be used with a context manager when sw ported to python3
  tmpdir = tempfile.mkdtemp(prefix='epublius_')
  
  # create epublius instances
  core = epublius.Epublius(tmpdir)
  parser = parse_tools.Parse_tools()

  args = core.argv

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

  data = metadata.Metadata(core.argv)
  html = output_html.Output_html(os.path.abspath('assets/template.xhtml'))


  # Unzip epub to tmpdir
  core.unzip_epub()
    
  # path where xhtml and folders are expected
  path = os.path.join(tmpdir, 'OEBPS')
  # Get a list of the ebook content files
  content_files = parser.parse_toc(os.path.join(path, 'toc.xhtml'))

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

  '''
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
  '''

  for index, content in enumerate(content_files):
    print('{}: {}'.format(index, content))

    m = data.get_metadata(index, content_files)

    processed_content = html.render_template(m)
    print(processed_content)
    print('----')
    
    
  

  # We recopy the file, since when we earlier copied the file it had
  # not yet been processed by epublius, but now it has.
  #
  # TODO PLEASE GET RID OF THIS REPETITION
  shutil.copy2(os.path.join(path, toc_file),
               os.path.join(path, landing_file))


  shutil.copy2(os.path.join(template_dir, 'includes', 'css', 'html-style.css'),
               os.path.join(target_directory, 'css'))

  shutil.copytree(os.path.join(template_dir, 'includes', 'JS'),
                  os.path.join(target_directory, 'JS'))

  shutil.copytree(os.path.join(template_dir, 'includes', 'logo'),
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
