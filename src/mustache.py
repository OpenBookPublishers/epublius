#!/usr/bin/env python2.7
from string import Template


class Mustache:
    '''
    Python implementation of mustache using standard libraries.

    It is declared python2.7, but it works seamlessly on python3.
    '''
    def __init__(self, template):
        self.template = Template(template)

    def substitute(self, args):
        '''
        Apply a (safe) substitution with the supplied arguments.
        '''
        return self.template.safe_substitute(args)

