#!/usr/bin/env python3

import os
import subprocess
import shutil
import tempfile
from epublius.epublius import Epublius
from epublius.metadata import Metadata
from epublius.output import Output


def main():

    # Destruction of the temporary directory on completion
    with tempfile.TemporaryDirectory(prefix='epublius_') as work_dir:

        # Create epublius instances
        epublius = Epublius(work_dir)
        metadata = Metadata(epublius.argv)
        output = Output(os.path.abspath('assets/template.xhtml'))


        # Unzip epub to tmpdir
        epublius.unzip_epub()
    
        # path where xhtml and folders are expected
        path = os.path.join(work_dir, 'OEBPS')
        # Get a list of the ebook content files
        content_files = metadata.parse_toc(os.path.join(path, 'toc.xhtml'))

        toc_file = 'contents.xhtml'
        landing_file = 'main.html'
        template_dir = epublius.argv.template


        for index, content in enumerate(content_files):
            print('{}: {}'.format(index, content))

            content_metadata = metadata.get_metadata(index, content_files)

            processed_content = output.render_template(content_metadata)
            print(processed_content)
            print('----')


        
        target_directory = epublius.argv.output
        os.makedirs(target_directory)
            
        shutil.copy2(os.path.join(path, toc_file),
                     os.path.join(path, landing_file))


        shutil.copytree(os.path.join(template_dir, 'includes'),
                        os.path.join(target_directory),
                        dirs_exist_ok=True)


    # ZIP OUTPUT FOLDER
    # if target_directory looks like:
    # ../htmlreader_output/978-1-78374-863-1/

    # -> base_dir = '978-1-78374-863-1'
    base_dir = target_directory.split('/')[-2]

    # -> root_dir = '../htmlreader_output'
    root_dir = '/'.join([target_directory.split('/')[0],
                         target_directory.split('/')[1]])

if __name__ == '__main__':
    main()
