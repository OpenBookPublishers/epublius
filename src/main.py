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


        # Get book contents
        contents = epublius.get_contents()

        output_directory = os.path.join(epublius.argv.output,
                                        epublius.argv.isbn)
        os.makedirs(output_directory)

        # Get book cover file path
        cover_filepath = epublius.get_cover_filepath()

        # Get book TOC file path
        TOC_filepath = epublius.get_TOC_filepath()


        for index, section in enumerate(contents):

            # Create an instance of Metadata
            metadata = Metadata(epublius.argv, work_dir,
                                index, contents)

            # Get book section data
            section_data = metadata.get_section_data()
            section_css = metadata.get_css()
            section_body_text = metadata.get_body_text()
            section_title = metadata.get_section_title()
            mathjax_support = metadata.mathjax_support(
                                os.path.abspath('assets/mathjax-cdn.html'))

            # Combine all the metadata into one large dictionary
            section_metadata = {
                # Section data
                **section_data,
                **section_css,
                **section_body_text,
                **section_title,

                # Book data
                **mathjax_support,
                **cover_filepath,
                **TOC_filepath
            }

            # Combine section_data with the page template
            processed_content = output.render_template(section_metadata)

            # Write output to file
            file_path = os.path.join(output_directory, section)
            output.write_file(processed_content, file_path)


        # Duplicate TOC file to output_directory/main.html
        epublius.duplicate_contents(TOC_filepath.get('TOC_filepath'))

        # Copy the subfolders of ./src/includes/ to output_directory
        epublius.copy_folders(os.path.abspath('./includes/'))

        # Copy the subfolders of ./src/assets/uikit to output_directory
        epublius.copy_folders(os.path.abspath('./assets/uikit/'))

        # Copy the subfolders of work_dir/ (such as images/ and fonts/)
        # to output_directory
        epublius.copy_folders(work_dir)


if __name__ == '__main__':
    main()
