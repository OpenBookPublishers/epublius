#!/usr/bin/env python3

import os
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

        # Unzip epub to work_dir
        epublius.unzip_epub()


        contents = epublius.get_contents()

        for index, content in enumerate(contents):
            print('{}: {}'.format(index, content))

            content_metadata = metadata.get_metadata(index, contents)

            processed_content = output.render_template(content_metadata)
            print(processed_content)
            print('----')



        oebps_path = os.path.join(work_dir, 'OEBPS')
            
        target_directory = epublius.argv.output
        os.makedirs(target_directory)
            
        # duplicate content.xhtml to main.html
        shutil.copy2(os.path.join(oebps_path, 'contents.xhtml'),
                     os.path.join(oebps_path, 'main.html'))


        # copy inclides to target directory
        shutil.copytree(os.path.join(os.getcwd(), 'includes'),
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
