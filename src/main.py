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
        output = Output(os.path.abspath('assets/template.xhtml'))

        # Unzip epub to work_dir
        epublius.unzip_epub()

        # Get book contents
        contents = epublius.get_contents()

        # Create an instance of Metadata
        metadata = Metadata(epublius.argv, contents, work_dir)
        
        target_directory = epublius.argv.output
        os.makedirs(target_directory)

        for index, file_name in enumerate(contents):

            # Get book section data
            section_data = metadata.get_section_data(index)
            section_css = metadata.get_css(index)
            section_body_text = metadata.get_body_text(index)
            section_breadcrumbs = metadata.get_breadcrumbs(index)

            # Combine all the metadata into one (python) dictionary
            section_metadata = {
                **section_data,
                **section_css,
                **section_body_text,
                **section_breadcrumbs
            }

            # Merge data into template
            processed_content = output.render_template(section_metadata)

            # Write to file
            file_path = os.path.join(epublius.argv.output, file_name)
            output.write_file(processed_content, file_path)
            


        oebps_path = os.path.join(work_dir, 'OEBPS')
            
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
