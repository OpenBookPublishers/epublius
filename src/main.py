#!/usr/bin/env python3

import os
import subprocess
import shutil
import tempfile
from epublius import epublius
from epublius import parse_tools
from epublius import metadata
from epublius import output_html


def main():

    # Destruction of the temporary directory on completion
    with tempfile.TemporaryDirectory(prefix='epublius_') as work_dir:

        # Create epublius instances
        core = epublius.Epublius(work_dir)
        parser = parse_tools.Parse_tools()

        data = metadata.Metadata(core.argv)
        html = output_html.Output_html(os.path.abspath('assets/template.xhtml'))


        # Unzip epub to tmpdir
        core.unzip_epub()
    
        # path where xhtml and folders are expected
        path = os.path.join(work_dir, 'OEBPS')
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
