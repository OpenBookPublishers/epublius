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

  data = metadata.Metadata(core.argv)
  html = output_html.Output_html(os.path.abspath('assets/template.xhtml'))


  # Unzip epub to tmpdir
  core.unzip_epub()
    
  # path where xhtml and folders are expected
  path = os.path.join(tmpdir, 'OEBPS')
  # Get a list of the ebook content files
  content_files = parser.parse_toc(os.path.join(path, 'toc.xhtml'))

  target_directory = core.argv.output
  os.makedirs(target_directory)

  toc_file = 'contents.xhtml'
  landing_file = 'main.html'
  template_dir = core.argv.template


  for index, content in enumerate(content_files):
    print('{}: {}'.format(index, content))

    m = data.get_metadata(index, content_files)

    processed_content = html.render_template(m)
    print(processed_content)
    print('----')
    
    
  

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
