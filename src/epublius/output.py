#!/usr/bin/env python3

from string import Template


class Output:
    '''
    Module to output xhtml files

    At present, the module reads a template file to combine with metadata
    using a mustache python implementation.
    '''
    
    def __init__(self, template_path):

        # Read the remplate file and create a Template object
        with open(template_path, 'r') as template_file:
            template_dump = template_file.read()

        self.template = Template(template_dump)

    def render_template(self, metadata):
        '''
        Get metadata from intput (python dictionary)
        return the template with the supplied metadata (str)
        '''

        return self.template.safe_substitute(metadata)



