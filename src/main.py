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

        # Unzip the 'OEBPS/' folder of the epub file to work_dir
        epublius.unzip_epub('OEBPS/')

        # Get book contents
        contents = epublius.get_contents()

        output_directory = os.path.join(epublius.argv.output,
                                        epublius.argv.isbn)
        os.makedirs(output_directory)

        # Get book cover file path
        cover_filepath = epublius.get_cover_filepath()


        for index, section in enumerate(contents):

            # Create an instance of Metadata
            metadata = Metadata(epublius.argv, work_dir,
                                index, contents)

            # Get book section data
            section_data = metadata.get_section_data()
            section_css = metadata.get_css()
            section_body_text = metadata.get_body_text()
            section_breadcrumbs = metadata.get_breadcrumbs()
            mathjax_support = metadata.mathjax_support()

            # Combine all the metadata into one large dictionary
            section_metadata = {
                **section_data,
                **section_css,
                **section_body_text,
                **section_breadcrumbs,
                **mathjax_support,
                **cover_filepath
            }

            # Combine section_data with the page template
            processed_content = output.render_template(section_metadata)

            # Write output to file
            file_path = os.path.join(output_directory, section)
            output.write_file(processed_content, file_path)


        # Duplicate output_directory/content.xhtml
        # to output_directory/main.html
        epublius.duplicate_contents()

        # Copy the subfolders of ./src/includes/ to output_directory
        epublius.copy_folders(os.path.abspath('./includes/'))

        # Copy the subfolders of ./src/assets/uikit to output_directory
        epublius.copy_folders(os.path.abspath('./assets/uikit/'))

        # Copy the subfolders of work_dir/ (such as images/ and fonts/)
        # to output_directory
        epublius.copy_folders(work_dir)


if __name__ == '__main__':
    main()
