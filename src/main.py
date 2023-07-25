#!/usr/bin/env python3

import os
import tempfile
from epublius.epublius import Epublius
from epublius.metadata import Metadata
from epublius.output import Output
from epublius.thoth import Thoth
from thothlibrary import ThothError


def main():

    # Destruction of the temporary directory on completion
    with tempfile.TemporaryDirectory(prefix='epublius_') as work_dir:

        # Create instances
        epublius = Epublius(work_dir)
        output = Output(os.path.abspath('assets/template.xhtml'))
        thoth = Thoth()

        # Warn if user requested to write URLs to Thoth but Thoth login failed
        if epublius.argv.write_urls and not thoth.logged_in:
            print('[WARNING] Thoth login failed; URLs will not be written')

        # Get book contents
        contents = epublius.get_contents()

        output_directory = os.path.join(epublius.argv.output,
                                        epublius.argv.doi)
        os.makedirs(output_directory)

        cover_filepath = epublius.get_cover_filepath()
        TOC_filepath = epublius.get_TOC_filepath()

        mathjax_cdn_filepath = os.path.abspath('assets/mathjax-cdn.html')


        for index, section in enumerate(contents):

            # Create an instance of Metadata
            metadata = Metadata(epublius.argv, work_dir,
                                index, contents)

            # Combine all the metadata into one large dictionary
            section_metadata = {
                # Section data
                **metadata.get_section_data(),
                **metadata.get_css(),
                **metadata.get_body_text(),
                **metadata.get_section_title(),

                # Book data
                **metadata.mathjax_support(mathjax_cdn_filepath),
                **cover_filepath,
                **TOC_filepath,
                **metadata.get_privacy_policy_url()
            }

            # Combine section_data with the page template
            processed_content = output.render_template(section_metadata)

            # Write output to file
            file_path = os.path.join(output_directory, section)
            output.write_file(processed_content, file_path)

            if epublius.argv.write_urls and thoth.logged_in:
                # Write chapter URL metadata to Thoth
                try:
                    thoth.write_urls(metadata, epublius.argv.doi)
                except (KeyError, ThothError) as e:
                    # Continue on error, but display warning
                    print('[WARNING] Error writing URLs to Thoth for {}: {}'.format(section, e))

        # Duplicate TOC file to output_directory/main.html
        epublius.duplicate_contents(TOC_filepath.get('TOC_filepath'))

        # Copy the subfolders of work_dir/ (such as images/ and fonts/)
        # to output_directory
        epublius.copy_folders(work_dir)


if __name__ == '__main__':
    main()
