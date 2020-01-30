#!/usr/bin/env python3

from string import Template


class Mustache:
    '''
    Python implementation of mustache using standard libraries.
    '''
    def __init__(self, template):
        self.template = Template(template)

    def substitute(self, args):
        '''
        Apply a (safe) substitution with the supplied arguments.
        '''
        return self.template.safe_substitute(args)

